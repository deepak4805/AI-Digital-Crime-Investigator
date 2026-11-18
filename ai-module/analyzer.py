import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment. Please set GEMINI_API_KEY.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def clean_json_response(response_text):
    if not response_text:
        return "{}"

    text = response_text.strip()

    # Remove markdown ```json ... ``` wrappers
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Try direct parse
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Extract first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    return "{}"


def analyze_with_gemini(prompt):
    if not gemini_client:
        raise RuntimeError("Gemini client not initialized. Check GEMINI_API_KEY.")

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3.1-flash-lite-preview",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash"
    ]

    last_err = None
    for model_name in models_to_try:
        try:
            print(f"Calling Gemini API with model: {model_name}...")
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return clean_json_response(response.text)
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_err = e

    raise last_err or RuntimeError("All Gemini models failed")


def analyze_evidence(text):
    if not text or not text.strip():
        return {
            "names": [],
            "phone_numbers": [],
            "bank_accounts": [],
            "amounts": [],
            "dates": [],
            "times": [],
            "urls": [],
            "upi_ids": [],
            "suspicious_indicators": [],
            "crime_patterns": [],
            "events": [],
            "risk_score": 0,
            "risk_level": "LOW",
            "risk_reason": "No evidence text provided.",
            "summary": "No text available to analyze."
        }

    prompt = (
        "You are an expert Digital Forensics & Cybercrime Investigator AI assistant.\n\n"
        "Carefully analyze the following digital evidence and extract investigative findings.\n\n"
        "RULES:\n"
        "1. Extract ONLY facts, names, phone numbers, bank accounts, amounts, dates, times, URLs, and UPI IDs present in the text.\n"
        "2. Identify suspicious indicators (urgency, threats, fake KYC, credential harvesting, unauthorized requests, impersonation).\n"
        "3. Identify crime patterns (e.g., Online Banking Fraud, Phishing, UPI Scams, Social Engineering, Identity Theft).\n"
        "4. Calculate an objective Risk Score between 0 and 100 based on the severity and presence of malicious indicators.\n"
        "   Risk Score Scale:\n"
        "   0 - 24: LOW\n"
        "   25 - 49: MEDIUM\n"
        "   50 - 74: HIGH\n"
        "   75 - 100: CRITICAL\n"
        "5. Provide a concise executive summary and risk rationale.\n"
        "6. Return ONLY a valid JSON object with EXACTLY this structure:\n\n"
        "{\n"
        '    "names": ["string"],\n'
        '    "phone_numbers": ["string"],\n'
        '    "bank_accounts": ["string"],\n'
        '    "amounts": ["string"],\n'
        '    "dates": ["string"],\n'
        '    "times": ["string"],\n'
        '    "urls": ["string"],\n'
        '    "upi_ids": ["string"],\n'
        '    "suspicious_indicators": ["string"],\n'
        '    "crime_patterns": ["string"],\n'
        '    "events": [\n'
        '        {\n'
        '            "date": "string or null",\n'
        '            "time": "string or null",\n'
        '            "event": "string"\n'
        '        }\n'
        '    ],\n'
        '    "risk_score": 75,\n'
        '    "risk_level": "HIGH",\n'
        '    "risk_reason": "Explanation of the calculated risk",\n'
        '    "summary": "Brief forensic summary of findings"\n'
        "}\n\n"
        f"EVIDENCE:\n{text}\n"
    )

    try:
        json_str = analyze_with_gemini(prompt)
        data = json.loads(json_str)

        default_keys = {
            "names": [], "phone_numbers": [], "bank_accounts": [],
            "amounts": [], "dates": [], "times": [], "urls": [], "upi_ids": [],
            "suspicious_indicators": [], "crime_patterns": [], "events": [],
            "risk_score": 0, "risk_level": "LOW", "risk_reason": "", "summary": ""
        }
        for k, v in default_keys.items():
            if k not in data:
                data[k] = v

        return data

    except Exception as e:
        print("Gemini analysis error:", e)
        # Rule-based fallback extraction if API is offline or key quota exhausted
        indicators = []
        lower_t = text.lower()
        if "kyc" in lower_t: indicators.append("Unverified KYC urgency claim")
        if "block" in lower_t or "suspend" in lower_t: indicators.append("Threat of account deactivation/blocking")
        if "upi" in lower_t or "pay" in lower_t or "send" in lower_t: indicators.append("Financial transfer demand")

        score = 65 if len(indicators) >= 2 else (35 if indicators else 15)
        level = "HIGH" if score >= 50 else ("MEDIUM" if score >= 25 else "LOW")

        return {
            "names": [],
            "phone_numbers": list(dict.fromkeys(re.findall(r"\+?\d{10,12}", text))),
            "bank_accounts": [],
            "amounts": list(dict.fromkeys(re.findall(r"(?:₹|Rs\.?|INR|USD|\$)\s*\d+(?:,\d+)*(?:\.\d+)?", text, re.IGNORECASE))),
            "dates": list(dict.fromkeys(re.findall(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text))),
            "times": list(dict.fromkeys(re.findall(r"\d{1,2}:\d{2}(?:\s*[ap]m)?", text, re.IGNORECASE))),
            "urls": list(dict.fromkeys(re.findall(r"https?://[^\s]+", text))),
            "upi_ids": list(dict.fromkeys(re.findall(r"[\w.-]+@[a-zA-Z]{2,}", text))),
            "suspicious_indicators": indicators or ["Automated heuristic pattern parsing"],
            "crime_patterns": ["Potential Cybercrime / Social Engineering"] if indicators else ["General Investigation"],
            "events": [{"date": None, "time": None, "event": "Evidence recorded"}],
            "risk_score": score,
            "risk_level": level,
            "risk_reason": f"Fallback rule-based forensic analysis (AI fallback: {str(e)})",
            "summary": "Evidence processed via heuristic parser."
        }


if __name__ == "__main__":
    sample = "Your bank account has been blocked due to KYC expiration. Send Rs. 5000 to fraud@upi immediately. Contact 9876543210."
    print("Running test...")
    res = analyze_evidence(sample)
    print(json.dumps(res, indent=2))

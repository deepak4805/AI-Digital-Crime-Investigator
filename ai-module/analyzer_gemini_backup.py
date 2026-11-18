import os
import json
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key NOT found")
    exit()

print("API key loaded successfully")

# Create Gemini client
client = genai.Client(api_key=api_key)


def analyze_evidence(text):

    prompt = f"""
You are an AI digital crime evidence analysis assistant.

Analyze the following digital evidence carefully.

IMPORTANT RULES:
- Extract only information that is actually present.
- Do not invent names, phone numbers, dates, transactions or other facts.
- If something is not present, return an empty list.
- Identify potentially suspicious indicators, but do not declare that a person is guilty.
- The analysis is only an aid for investigators.

Extract the following:

1. Person names
2. Phone numbers
3. Email addresses
4. UPI IDs
5. Bank/account information
6. Transaction amounts
7. Dates
8. Times
9. URLs
10. Suspicious indicators
11. Important events
12. Short evidence summary
13. Potential crime/scam patterns
14. Risk score from 0 to 100
15. Risk level: LOW, MEDIUM, HIGH, or CRITICAL
16. Reason for the risk level

Return ONLY valid JSON.

Use exactly this structure:

{{

    "persons": [],
    "phone_numbers": [],
    "emails": [],
    "upi_ids": [],
    "bank_accounts": [],
    "amounts": [],
    "dates": [],
    "times": [],
    "urls": [],
    "suspicious_indicators": [],
    "crime_patterns": [],
    "events": [],
    "risk_score": 0,
    "risk_level": "",
    "risk_reason": "",
    "summary": ""
}}

DIGITAL EVIDENCE:
{text}

Identify potential scam or crime patterns such as:

- phishing
- fake KYC/account verification
- impersonation
- payment fraud
- investment scam
- threatening messages
- suspicious links
- identity theft indicators
- unauthorized transaction
- social engineering

Do not claim that a crime definitely occurred.
Use terms such as "potentially suspicious" or "possible fraud indicator".

Calculate a risk score from 0 to 100 based only on the evidence.

Risk levels:
0-24 = LOW
25-49 = MEDIUM
50-74 = HIGH
75-100 = CRITICAL
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# Test the analyzer
if __name__ == "__main__":

    sample_text = """
    Rahul:
    Your KYC has expired.

    Send Rs. 5000 immediately to abc@upi
    to reactivate your account.

    Contact: 9876543210
    Email: support@example.com

    Website: http://example.com

    Date: 08/08/2026
    """

    result = analyze_evidence(sample_text)

    print("\n===== AI EVIDENCE ANALYSIS =====\n")
    print(result)
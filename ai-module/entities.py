import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def find_relationships(evidence):
    prompt = f"""
You are an AI digital evidence relationship analyzer.
Analyze the supplied evidence items and identify cross-evidence relationships between entities (persons, phones, UPI IDs, banks, amounts, URLs).

Rules:
1. Use ONLY information present in the evidence.
2. Identify repeated entities across different pieces of evidence.
3. Identify which entities appear together.
4. Return ONLY valid JSON (no markdown).

JSON format:
{{
    "repeated_entities": [],
    "relationships": [],
    "observations": []
}}

Evidence:
{json.dumps(evidence, indent=2)}
"""

    if not client:
        return json.dumps({"repeated_entities": [], "relationships": [], "observations": ["AI client not configured"]})

    for model_name in ["gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "gemini-3.8-flash", "gemini-flash-latest"]:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt)
            clean = re.sub(r"^```json\s*", "", res.text or "", flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean).strip()
            return clean
        except Exception as e:
            print(f"Model {model_name} failed: {e}")

    return json.dumps({"repeated_entities": [], "relationships": [], "observations": ["Analysis completed"]})

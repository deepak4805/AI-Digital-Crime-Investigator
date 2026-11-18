import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def create_timeline(events):
    prompt = f"""
You are an AI digital evidence timeline generator.
Arrange the following investigation events in chronological order.

Rules:
- Use only the information provided.
- If date/time is missing, keep it as null.
- Return ONLY valid JSON array with oldest event first.

Format:
[
    {{
        "date": "string or null",
        "time": "string or null",
        "event": "string"
    }}
]

Events:
{json.dumps(events, indent=2)}
"""

    if not client:
        return json.dumps(events)

    for model_name in ["gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "gemini-3.8-flash", "gemini-flash-latest"]:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt)
            clean = re.sub(r"^```json\s*", "", res.text or "", flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean).strip()
            return clean
        except Exception as e:
            print(f"Model {model_name} failed: {e}")

    return json.dumps(events)

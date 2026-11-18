from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_evidence

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "AI Digital Crime Investigator - AI Microservice is running on port 5001!"


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get("text", "")).strip()

        if not text:
            return jsonify({
                "status": "error",
                "message": "No evidence text provided"
            }), 400

        print("\n========== AI EVIDENCE ANALYSIS ==========")
        print(f"Evidence text ({len(text)} chars): {text[:120]}...")

        result = analyze_evidence(text)

        print(f"Result: Risk Level = {result.get('risk_level')}, Score = {result.get('risk_score')}")
        print("==========================================\n")

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except Exception as e:
        print("ANALYSIS ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    print("==================================================")
    print(" AI DIGITAL CRIME INVESTIGATOR - AI MODULE (Port 5001)")
    print("==================================================")
    app.run(host="0.0.0.0", port=5001, debug=True)

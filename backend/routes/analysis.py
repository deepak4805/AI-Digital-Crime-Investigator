import os
import json
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from models import Case, Evidence, Analysis

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")

AI_MODULE_URL = os.getenv("AI_MODULE_URL", "http://127.0.0.1:5001/analyze")


@analysis_bp.route("/", methods=["POST"])
@jwt_required()
def analyze():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    text = str(data.get("text", "")).strip()
    case_id = data.get("case_id")
    evidence_id = data.get("evidence_id")

    if not text:
        return jsonify({
            "success": False,
            "message": "Evidence text is required for analysis"
        }), 400

    # Call AI module
    try:
        response = requests.post(
            AI_MODULE_URL,
            json={"text": text},
            timeout=120
        )

        if not response.ok:
            return jsonify({
                "success": False,
                "message": "AI Analysis module error",
                "detail": response.text
            }), 502

        ai_data = response.json()
        result = ai_data.get("result", {})

    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "message": "AI Module is not running on port 5001. Please ensure the AI service is started."
        }), 503
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"AI request failed: {str(e)}"
        }), 500

    # Persist if linked to a valid case
    if case_id:
        case = Case.query.filter_by(id=case_id, user_id=user_id).first()
        if case and isinstance(result, dict):
            risk_score = result.get("risk_score", 0)
            risk_level = result.get("risk_level", "UNKNOWN")

            analysis_record = Analysis(
                case_id=case_id,
                evidence_id=evidence_id,
                result_json=json.dumps(result),
                risk_level=risk_level,
                risk_score=int(risk_score) if isinstance(risk_score, (int, float)) else 0
            )

            db.session.add(analysis_record)
            db.session.commit()

    return jsonify({
        "success": True,
        "result": result
    }), 200


@analysis_bp.route("/case/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_analyses(case_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    analyses = Analysis.query.filter_by(case_id=case_id).order_by(Analysis.analyzed_at.desc()).all()

    results = []
    for a in analyses:
        try:
            parsed = json.loads(a.result_json)
        except Exception:
            parsed = {}
        results.append({
            "id": a.id,
            "case_id": a.case_id,
            "evidence_id": a.evidence_id,
            "risk_level": a.risk_level,
            "risk_score": a.risk_score,
            "result": parsed,
            "analyzed_at": a.analyzed_at.isoformat() if a.analyzed_at else None
        })

    return jsonify({
        "success": True,
        "analyses": results
    }), 200

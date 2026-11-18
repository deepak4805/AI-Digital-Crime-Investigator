import json
from collections import defaultdict
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Case, Evidence, Analysis

entities_bp = Blueprint("entities", __name__, url_prefix="/api")

ENTITY_FIELDS = [
    ("phone_numbers", "Phone Number", "📞"),
    ("urls", "URL", "🔗"),
    ("upi_ids", "UPI ID", "💳"),
    ("bank_accounts", "Bank Account", "🏦"),
    ("names", "Person Name", "👤")
]


@entities_bp.route("/evidence", methods=["GET"])
@jwt_required()
def get_all_evidence():
    user_id = int(get_jwt_identity())

    evidence_list = (
        Evidence.query
        .join(Case, Evidence.case_id == Case.id)
        .filter(Case.user_id == user_id)
        .order_by(Evidence.uploaded_at.asc())
        .all()
    )

    result = [{
        "id": ev.id,
        "name": ev.filename,
        "filename": ev.filename,
        "type": ev.file_type,
        "size": ev.size_bytes,
        "size_bytes": ev.size_bytes,
        "sha256_hash": ev.sha256_hash,
        "extracted_text": ev.extracted_text,
        "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None,
        "case_id": ev.case_id
    } for ev in evidence_list]

    return jsonify({
        "success": True,
        "count": len(result),
        "evidence": result
    }), 200


@entities_bp.route("/entities/suspicious", methods=["GET"])
@jwt_required()
def get_suspicious_entities():
    user_id = int(get_jwt_identity())

    analyses = (
        Analysis.query
        .join(Case, Analysis.case_id == Case.id)
        .filter(Case.user_id == user_id)
        .all()
    )

    occurrences = defaultdict(set)

    for analysis in analyses:
        try:
            res = json.loads(analysis.result_json)
        except Exception:
            continue

        if not isinstance(res, dict):
            continue

        for field, label, icon in ENTITY_FIELDS:
            items = res.get(field, [])
            if not isinstance(items, list):
                continue

            for val in items:
                if val and isinstance(val, (str, int, float)):
                    sval = str(val).strip()
                    if sval:
                        occurrences[(field, sval)].add(analysis.evidence_id or analysis.id)

    suspicious_list = []
    for (field, val), ev_ids in occurrences.items():
        suspicious_list.append({
            "type": field,
            "value": val,
            "count": len(ev_ids),
            "is_flagged": len(ev_ids) >= 2
        })

    suspicious_list.sort(key=lambda x: x["count"], reverse=True)

    return jsonify({
        "success": True,
        "count": len(suspicious_list),
        "suspicious_entities": suspicious_list
    }), 200

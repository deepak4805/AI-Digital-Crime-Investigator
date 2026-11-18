from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from models import Case, Evidence, Analysis

cases_bp = Blueprint("cases", __name__, url_prefix="/api/cases")


@cases_bp.route("/", methods=["POST"])
@jwt_required()
def create_case():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip() if data.get("description") else None

    if not title:
        return jsonify({
            "success": False,
            "message": "Case title is required"
        }), 400

    new_case = Case(
        title=title,
        description=description,
        user_id=user_id
    )

    db.session.add(new_case)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Case created successfully",
        "case": {
            "id": new_case.id,
            "title": new_case.title,
            "description": new_case.description,
            "status": new_case.status,
            "created_at": new_case.created_at.isoformat() if new_case.created_at else None,
            "user_id": new_case.user_id,
            "evidence_count": 0
        }
    }), 201


@cases_bp.route("/", methods=["GET"])
@jwt_required()
def get_cases():
    user_id = int(get_jwt_identity())
    cases = Case.query.filter_by(user_id=user_id).order_by(Case.created_at.desc()).all()

    case_list = []
    for c in cases:
        ev_count = Evidence.query.filter_by(case_id=c.id).count()
        last_analysis = Analysis.query.filter_by(case_id=c.id).order_by(Analysis.analyzed_at.desc()).first()
        case_list.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "user_id": c.user_id,
            "evidence_count": ev_count,
            "latest_risk_level": last_analysis.risk_level if last_analysis else None,
            "latest_risk_score": last_analysis.risk_score if last_analysis else None
        })

    return jsonify({
        "success": True,
        "cases": case_list
    }), 200


@cases_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case(case_id):
    user_id = int(get_jwt_identity())
    c = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not c:
        return jsonify({
            "success": False,
            "message": "Case not found"
        }), 404

    evidence_items = Evidence.query.filter_by(case_id=c.id).order_by(Evidence.uploaded_at.desc()).all()
    ev_list = [{
        "id": ev.id,
        "filename": ev.filename,
        "file_type": ev.file_type,
        "size_bytes": ev.size_bytes,
        "sha256_hash": ev.sha256_hash,
        "extracted_text": ev.extracted_text,
        "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None
    } for ev in evidence_items]

    return jsonify({
        "success": True,
        "case": {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "user_id": c.user_id,
            "evidence": ev_list
        }
    }), 200


@cases_bp.route("/<int:case_id>", methods=["PUT"])
@jwt_required()
def update_case(case_id):
    user_id = int(get_jwt_identity())
    c = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not c:
        return jsonify({
            "success": False,
            "message": "Case not found"
        }), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        t = str(data["title"]).strip()
        if t:
            c.title = t
    if "description" in data:
        c.description = str(data["description"]).strip()
    if "status" in data:
        c.status = str(data["status"]).strip()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Case updated successfully",
        "case": {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "user_id": c.user_id
        }
    }), 200


@cases_bp.route("/<int:case_id>", methods=["DELETE"])
@jwt_required()
def delete_case(case_id):
    user_id = int(get_jwt_identity())
    c = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not c:
        return jsonify({
            "success": False,
            "message": "Case not found"
        }), 404

    db.session.delete(c)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Case deleted successfully"
    }), 200

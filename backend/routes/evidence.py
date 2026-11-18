import os
import hashlib
import uuid
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from database import db
from models import Case, Evidence

evidence_bp = Blueprint("evidence", __name__, url_prefix="/api/cases")

UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "uploads")
)

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "webp", "bmp", "tiff",
    "pdf", "txt", "doc", "docx", "csv", "log", "json",
    "mp3", "wav", "m4a", "ogg"
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def extract_evidence_text(filepath, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    extracted = ""

    # Plain text files
    if ext in ["txt", "log", "csv", "json"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                extracted = f.read()
        except Exception as e:
            print("Text read error:", e)

    # PDF documents
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            text_pages = [page.extract_text() or "" for page in reader.pages]
            extracted = "\n".join(text_pages).strip()
        except Exception as e:
            print("PDF extract error:", e)

    # Images via OCR
    elif ext in ["png", "jpg", "jpeg", "webp", "bmp", "tiff"]:
        try:
            import pytesseract
            from PIL import Image

            # Try common Windows tesseract locations
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\deepa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
            ]
            for p in common_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break

            img = Image.open(filepath)
            extracted = pytesseract.image_to_string(img).strip()
        except Exception as e:
            print("OCR extract error:", e)

    # Audio transcription via Whisper
    elif ext in ["mp3", "wav", "m4a", "ogg"]:
        try:
            import whisper
            model = whisper.load_model("base")
            res = model.transcribe(filepath)
            extracted = res.get("text", "").strip()
        except Exception as e:
            print("Audio transcribe error:", e)

    return extracted.strip()


@evidence_bp.route("/<int:case_id>/evidence/upload", methods=["POST"])
@jwt_required()
def upload_evidence(case_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file attached"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "File type not supported"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    unique_suffix = uuid.uuid4().hex[:8]
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "dat"
    original_filename = secure_filename(file.filename) or f"evidence_{unique_suffix}.{ext}"
    stored_filename = f"{case_id}_{unique_suffix}_{original_filename}"
    filepath = os.path.join(UPLOAD_FOLDER, stored_filename)

    file.save(filepath)

    size_bytes = os.path.getsize(filepath)
    sha256_hash = compute_sha256(filepath)
    file_type = file.content_type or "application/octet-stream"

    # Auto extract text (OCR / PDF / text / Audio)
    extracted_text = extract_evidence_text(filepath, original_filename)

    new_evidence = Evidence(
        filename=original_filename,
        stored_filename=stored_filename,
        filepath=filepath,
        file_type=file_type,
        size_bytes=size_bytes,
        sha256_hash=sha256_hash,
        extracted_text=extracted_text,
        case_id=case_id
    )

    db.session.add(new_evidence)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Evidence uploaded and processed successfully",
        "evidence": {
            "id": new_evidence.id,
            "filename": new_evidence.filename,
            "stored_filename": new_evidence.stored_filename,
            "file_type": new_evidence.file_type,
            "size_bytes": new_evidence.size_bytes,
            "sha256_hash": new_evidence.sha256_hash,
            "extracted_text": new_evidence.extracted_text,
            "uploaded_at": new_evidence.uploaded_at.isoformat() if new_evidence.uploaded_at else None,
            "case_id": new_evidence.case_id
        }
    }), 201


@evidence_bp.route("/<int:case_id>/evidence", methods=["GET"])
@jwt_required()
def get_case_evidence(case_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    evidence_list = Evidence.query.filter_by(case_id=case_id).order_by(Evidence.uploaded_at.desc()).all()

    return jsonify({
        "success": True,
        "evidence": [{
            "id": ev.id,
            "filename": ev.filename,
            "stored_filename": ev.stored_filename,
            "file_type": ev.file_type,
            "size_bytes": ev.size_bytes,
            "sha256_hash": ev.sha256_hash,
            "extracted_text": ev.extracted_text,
            "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None,
            "case_id": ev.case_id
        } for ev in evidence_list]
    }), 200


@evidence_bp.route("/<int:case_id>/evidence/<int:evidence_id>", methods=["GET"])
@jwt_required()
def get_single_evidence(case_id, evidence_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()

    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    ev = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first()
    if not ev:
        return jsonify({"success": False, "message": "Evidence not found"}), 404

    return jsonify({
        "success": True,
        "evidence": {
            "id": ev.id,
            "filename": ev.filename,
            "stored_filename": ev.stored_filename,
            "file_type": ev.file_type,
            "size_bytes": ev.size_bytes,
            "sha256_hash": ev.sha256_hash,
            "extracted_text": ev.extracted_text,
            "uploaded_at": ev.uploaded_at.isoformat() if ev.uploaded_at else None,
            "case_id": ev.case_id
        }
    }), 200


@evidence_bp.route("/<int:case_id>/evidence/<int:evidence_id>/ocr", methods=["POST"])
@jwt_required()
def run_ocr_on_evidence(case_id, evidence_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    ev = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first()
    if not ev:
        return jsonify({"success": False, "message": "Evidence not found"}), 404

    extracted = extract_evidence_text(ev.filepath, ev.filename)
    ev.extracted_text = extracted
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "OCR / text extraction completed",
        "extracted_text": extracted
    }), 200


@evidence_bp.route("/<int:case_id>/evidence/<int:evidence_id>/file", methods=["GET"])
@jwt_required()
def get_evidence_file(case_id, evidence_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    ev = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first()
    if not ev or not os.path.exists(ev.filepath):
        return jsonify({"success": False, "message": "File not found"}), 404

    return send_file(ev.filepath, download_name=ev.filename, as_attachment=False)


@evidence_bp.route("/<int:case_id>/evidence/<int:evidence_id>", methods=["DELETE"])
@jwt_required()
def delete_evidence(case_id, evidence_id):
    user_id = int(get_jwt_identity())
    case = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    ev = Evidence.query.filter_by(id=evidence_id, case_id=case_id).first()
    if not ev:
        return jsonify({"success": False, "message": "Evidence not found"}), 404

    if os.path.exists(ev.filepath):
        try:
            os.remove(ev.filepath)
        except Exception as e:
            print("File delete error:", e)

    db.session.delete(ev)
    db.session.commit()

    return jsonify({"success": True, "message": "Evidence deleted successfully"}), 200

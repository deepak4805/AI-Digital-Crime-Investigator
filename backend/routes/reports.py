import os
import json
import html
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from database import db
from models import Case, Evidence, Analysis, Report

reports_bp = Blueprint("reports", __name__, url_prefix="/api")

REPORT_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "reports")
)
os.makedirs(REPORT_FOLDER, exist_ok=True)


@reports_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_reports():
    user_id = int(get_jwt_identity())
    reports = (
        Report.query
        .join(Case, Report.case_id == Case.id)
        .filter(Case.user_id == user_id)
        .order_by(Report.generated_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "reports": [{
            "id": r.id,
            "filename": r.filename,
            "case_id": r.case_id,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            "download_url": f"/api/reports/download/{r.filename}"
        } for r in reports]
    }), 200


@reports_bp.route("/report/generate", methods=["POST"])
@jwt_required()
def generate_report():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")

    # If no case_id passed, pick the user's latest case
    if not case_id:
        latest_case = Case.query.filter_by(user_id=user_id).order_by(Case.created_at.desc()).first()
        if not latest_case:
            return jsonify({"success": False, "message": "No case found to generate report for"}), 404
        case_id = latest_case.id

    case = Case.query.filter_by(id=case_id, user_id=user_id).first()
    if not case:
        return jsonify({"success": False, "message": "Case not found"}), 404

    evidence_list = Evidence.query.filter_by(case_id=case.id).all()
    analyses = Analysis.query.filter_by(case_id=case.id).order_by(Analysis.analyzed_at.desc()).all()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"AIDCI_Case_{case.id}_Report_{timestamp}.pdf"
    filepath = os.path.join(REPORT_FOLDER, filename)

    try:
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6
        )

        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        badge_style = ParagraphStyle(
            "BadgeStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.white
        )

        story = []

        # Header Title
        story.append(Paragraph("DIGITAL CRIME INVESTIGATION REPORT", title_style))
        story.append(Paragraph("AI-Assisted Forensics &amp; Evidence Analysis System", body_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

        # Case Metadata Table
        case_title_clean = html.escape(case.title or "Untitled Case")
        case_desc_clean = html.escape(case.description or "No description provided")
        case_data = [
            [Paragraph("<b>Case ID:</b>", body_style), Paragraph(str(case.id), body_style),
             Paragraph("<b>Status:</b>", body_style), Paragraph(html.escape(case.status.upper()), body_style)],
            [Paragraph("<b>Case Title:</b>", body_style), Paragraph(case_title_clean, body_style),
             Paragraph("<b>Generated:</b>", body_style), Paragraph(datetime.now().strftime("%d %b %Y, %H:%M"), body_style)],
            [Paragraph("<b>Description:</b>", body_style), Paragraph(case_desc_clean, body_style),
             Paragraph("<b>Evidence Count:</b>", body_style), Paragraph(str(len(evidence_list)), body_style)]
        ]

        t_case = Table(case_data, colWidths=[80, 180, 80, 180])
        t_case.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t_case)
        story.append(Spacer(1, 14))

        # Latest AI Analysis Summary
        story.append(Paragraph("1. AI Analysis &amp; Risk Assessment", h2_style))
        if analyses:
            latest = analyses[0]
            try:
                res = json.loads(latest.result_json)
            except Exception:
                res = {}

            risk_level = str(res.get("risk_level", "UNKNOWN")).upper()
            risk_score = res.get("risk_score", 0)

            # Color for risk
            risk_bg = colors.HexColor("#dc2626") if risk_level == "CRITICAL" or risk_score >= 75 else \
                      colors.HexColor("#ea580c") if risk_level == "HIGH" or risk_score >= 50 else \
                      colors.HexColor("#ca8a04") if risk_level == "MEDIUM" or risk_score >= 25 else \
                      colors.HexColor("#16a34a")

            summary_text = res.get("summary", "No automated summary provided.")
            reason_text = res.get("risk_reason", "No risk rationale provided.")

            risk_data = [
                [Paragraph("<b>Assessed Risk Level:</b>", body_style),
                 Paragraph(f"<b>{html.escape(risk_level)} (Score: {risk_score}/100)</b>", badge_style)],
                [Paragraph("<b>Executive Summary:</b>", body_style), Paragraph(html.escape(str(summary_text)), body_style)],
                [Paragraph("<b>Risk Rationale:</b>", body_style), Paragraph(html.escape(str(reason_text)), body_style)]
            ]

            t_risk = Table(risk_data, colWidths=[120, 400])
            t_risk.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), risk_bg),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t_risk)
            story.append(Spacer(1, 10))

            # Suspicious Indicators & Patterns
            indicators = res.get("suspicious_indicators", [])
            patterns = res.get("crime_patterns", [])

            if indicators:
                story.append(Paragraph("<b>Flagged Indicators:</b>", body_style))
                for ind in indicators:
                    story.append(Paragraph(f"&bull; {html.escape(str(ind))}", body_style))
                story.append(Spacer(1, 6))

            if patterns:
                story.append(Paragraph("<b>Crime Patterns Detected:</b>", body_style))
                for pat in patterns:
                    story.append(Paragraph(f"&bull; {html.escape(str(pat))}", body_style))
                story.append(Spacer(1, 10))

        else:
            story.append(Paragraph("<i>No AI analysis has been performed for this case yet.</i>", body_style))
            story.append(Spacer(1, 10))

        # Evidence Chain of Custody Table
        story.append(Paragraph("2. Evidence Inventory &amp; Digital Hash Registry", h2_style))
        if evidence_list:
            ev_table_data = [["ID", "Filename", "Type", "Size", "SHA-256 Hash"]]
            for ev in evidence_list:
                size_str = f"{round((ev.size_bytes or 0)/1024, 1)} KB"
                hash_short = (ev.sha256_hash[:20] + "...") if ev.sha256_hash else "N/A"
                ev_table_data.append([
                    str(ev.id),
                    ev.filename[:24],
                    (ev.file_type or "Unknown")[:18],
                    size_str,
                    hash_short
                ])

            t_ev = Table(ev_table_data, colWidths=[30, 140, 100, 60, 190])
            t_ev.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t_ev)
            story.append(Spacer(1, 12))

            # Extracted Text / OCR Summary
            story.append(Paragraph("3. Extracted Text / OCR Findings", h2_style))
            has_text = False
            for ev in evidence_list:
                if ev.extracted_text:
                    has_text = True
                    fn_clean = html.escape(ev.filename)
                    story.append(Paragraph(f"<b>Evidence #{ev.id} - {fn_clean}:</b>", body_style))
                    raw_snippet = ev.extracted_text[:400] + ("..." if len(ev.extracted_text) > 400 else "")
                    snippet = html.escape(raw_snippet)
                    story.append(Paragraph(f"<i>{snippet}</i>", body_style))
                    story.append(Spacer(1, 4))
            if not has_text:
                story.append(Paragraph("<i>No text or OCR content extracted.</i>", body_style))
        else:
            story.append(Paragraph("<i>No evidence files uploaded to this case.</i>", body_style))

        # Legal Disclaimer Footer
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))
        story.append(Paragraph(
            "<b>Disclaimer:</b> This report is generated by the AI Digital Crime Investigator platform. "
            "Findings and risk scores are assistive analytical assessments and should be corroborated with formal forensic validation.",
            ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=7, leading=9, textColor=colors.HexColor("#64748b"))
        ))

        doc.build(story)

        # Save Report in Database
        report_record = Report(
            case_id=case.id,
            filename=filename,
            filepath=filepath
        )
        db.session.add(report_record)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Report generated successfully",
            "filename": filename,
            "download_url": f"/api/reports/download/{filename}"
        }), 201

    except Exception as e:
        print("REPORT GENERATION ERROR:", str(e))
        return jsonify({
            "success": False,
            "message": f"Failed to generate PDF report: {str(e)}"
        }), 500


@reports_bp.route("/reports/download/<path:filename>", methods=["GET"])
def download_report(filename):
    try:
        return send_from_directory(REPORT_FOLDER, filename, as_attachment=False)
    except Exception as e:
        return jsonify({"success": False, "message": "Report file not found"}), 404


@reports_bp.route("/reports/<int:report_id>", methods=["DELETE"])
@jwt_required()
def delete_report(report_id):
    user_id = int(get_jwt_identity())
    report = (
        Report.query
        .join(Case, Report.case_id == Case.id)
        .filter(Report.id == report_id, Case.user_id == user_id)
        .first()
    )

    if not report:
        return jsonify({"success": False, "message": "Report not found"}), 404

    if os.path.exists(report.filepath):
        try:
            os.remove(report.filepath)
        except Exception:
            pass

    db.session.delete(report)
    db.session.commit()

    return jsonify({"success": True, "message": "Report deleted successfully"}), 200

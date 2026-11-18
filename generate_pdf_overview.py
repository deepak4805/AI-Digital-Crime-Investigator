import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "AI Digital Crime Investigator (AIDCI) — Comprehensive Project Specification")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — DIGITAL FORENSICS PLATFORM")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 44, letter[0] - 54, 44)
        self.restoreState()


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold"
    )

    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("AI DIGITAL CRIME INVESTIGATOR (AIDCI)", title_style))
    story.append(Paragraph("TECHNICAL SPECIFICATION, ARCHITECTURE & PLATFORM OVERVIEW", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=12))

    # Meta Info Card
    meta_data = [
        [Paragraph("<b>Document Version:</b> 1.0 (Production)", table_cell_style),
         Paragraph("<b>Classification:</b> Digital Forensics Architecture", table_cell_style)],
        [Paragraph("<b>Target System:</b> Full-Stack Cyber Investigation Platform", table_cell_style),
         Paragraph("<b>Core Intelligence:</b> Google Gemini API + OCR + Whisper", table_cell_style)],
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary & Purpose", h1_style))
    story.append(Paragraph(
        "The <b>AI Digital Crime Investigator (AIDCI)</b> is a specialized, modern digital forensics workspace "
        "engineered for law enforcement officers, cybercrime response units, and investigative analysts. "
        "The system solves the critical bottleneck of manually triaging vast streams of digital evidence "
        "(fraudulent chat screenshots, threatening voicemails, extortion emails, fake bank notices, and phishing portals). "
        "By pairing automated optical extraction and voice transcription with advanced Gemini LLM intelligence, "
        "AIDCI extracts actionable entities, quantifies threat severity, correlates serial fraud rings, "
        "and compiles court-admissible forensic documentation in seconds.",
        body_style
    ))

    # Section 2: System Architecture
    story.append(Paragraph("2. 3-Tier Microservice Topology", h1_style))
    story.append(Paragraph(
        "AIDCI employs a decoupled, asynchronous microservices architecture running across three dedicated ports:",
        body_style
    ))

    arch_data = [
        [Paragraph("Tier / Service", table_header_style), Paragraph("Port", table_header_style), Paragraph("Runtime / Stack", table_header_style), Paragraph("Core Responsibility", table_header_style)],
        [
            Paragraph("<b>Frontend SPA</b>", table_cell_bold),
            Paragraph("5173", table_cell_style),
            Paragraph("React 19, Vite 8, React Router v7", table_cell_style),
            Paragraph("Investigator UI, case switching, live upload, interactive dashboards, timeline view, and PDF downloads.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend REST API</b>", table_cell_bold),
            Paragraph("5000", table_cell_style),
            Paragraph("Flask 3.1, SQLite, SQLAlchemy 2.0, JWT", table_cell_style),
            Paragraph("Authentication, case management, SHA-256 digital custody hashing, entity aggregation, and ReportLab PDF compilation.", table_cell_style)
        ],
        [
            Paragraph("<b>AI Microservice</b>", table_cell_bold),
            Paragraph("5001", table_cell_style),
            Paragraph("Flask, google-genai, Tesseract, Whisper", table_cell_style),
            Paragraph("Multimodal extraction (Tesseract OCR, Whisper voice STT), Gemini intelligence evaluation, and regex fallback parsing.", table_cell_style)
        ],
    ]
    t_arch = Table(arch_data, colWidths=[90, 36, 150, 228])
    t_arch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Section 3: Technology Stack Details
    story.append(Paragraph("3. Detailed Technology Inventory", h1_style))

    tech_data = [
        [Paragraph("Component", table_header_style), Paragraph("Technology Used", table_header_style), Paragraph("Purpose / Implementation Details", table_header_style)],
        [
            Paragraph("<b>User Interface</b>", table_cell_bold),
            Paragraph("React 19.2 + Vite 8.2", table_cell_style),
            Paragraph("Fast, reactive component rendering with strict ESLint conformance and scoped cyber-dark styling.", table_cell_style)
        ],
        [
            Paragraph("<b>Routing & Navigation</b>", table_cell_bold),
            Paragraph("React Router v7", table_cell_style),
            Paragraph("Client-side routing with route guards (ProtectedRoute) managing investigator session states.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend Server</b>", table_cell_bold),
            Paragraph("Flask 3.1.3 + Werkzeug 3.1", table_cell_style),
            Paragraph("Lightweight, high-performance WSGI micro-framework organizing Blueprints for modular route segregation.", table_cell_style)
        ],
        [
            Paragraph("<b>Security & Auth</b>", table_cell_bold),
            Paragraph("Flask-JWT-Extended + PyJWT", table_cell_style),
            Paragraph("Stateless cryptographic bearer token authentication. Salted PBKDF2-SHA256 password security.", table_cell_style)
        ],
        [
            Paragraph("<b>Database & ORM</b>", table_cell_bold),
            Paragraph("SQLite + SQLAlchemy 2.0", table_cell_style),
            Paragraph("Zero-configuration persistent SQL database. Models with foreign keys, index optimization, and cascading deletions.", table_cell_style)
        ],
        [
            Paragraph("<b>AI / LLM Engine</b>", table_cell_bold),
            Paragraph("Google Gemini API (google-genai 2.17)", table_cell_style),
            Paragraph("Models: gemini-3.5-flash-lite, gemini-3-flash-preview, gemini-3.8-flash. JSON structured outputs.", table_cell_style)
        ],
        [
            Paragraph("<b>Optical Recognition</b>", table_cell_bold),
            Paragraph("Tesseract-OCR 5.5 + pytesseract", table_cell_style),
            Paragraph("Automated extraction of textual messages, phone numbers, and transaction IDs from uploaded images.", table_cell_style)
        ],
        [
            Paragraph("<b>Speech-to-Text</b>", table_cell_bold),
            Paragraph("OpenAI Whisper (Base) + ffmpeg", table_cell_style),
            Paragraph("Neural acoustic model transcribing incoming voicemails, call recordings (.mp3, .wav, .m4a, .ogg) to text.", table_cell_style)
        ],
        [
            Paragraph("<b>PDF Report Engine</b>", table_cell_bold),
            Paragraph("ReportLab 5.0", table_cell_style),
            Paragraph("Dynamic generation of official forensic investigation reports with styled flowables, tables, and headers.", table_cell_style)
        ],
        [
            Paragraph("<b>Evidence Hashing</b>", table_cell_bold),
            Paragraph("Python hashlib (SHA-256)", table_cell_style),
            Paragraph("Cryptographic 256-bit hash fingerprinting computed over 64KB stream chunks upon evidence ingestion.", table_cell_style)
        ]
    ]
    t_tech = Table(tech_data, colWidths=[100, 140, 264])
    t_tech.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # Section 4: Forensic Capabilities & Workflow
    story.append(Paragraph("4. Core Forensic Capabilities & Investigation Workflow", h1_style))
    
    story.append(Paragraph("<b>A. Multimodal Evidence Ingestion & Normalization</b>", h2_style))
    story.append(Paragraph(
        "• <b>Image OCR:</b> Ingests PNG, JPG, WEBP, BMP, and TIFF screenshots. Tesseract converts visual chat dialogues into UTF-8 text.<br/>"
        "• <b>Voice Transcription:</b> Ingests audio voicemails. OpenAI Whisper converts audio streams into verbatim forensic transcripts.<br/>"
        "• <b>Document Parsing:</b> Ingests PDFs, server logs, CSVs, and JSON files via pypdf and native stream readers.<br/>"
        "• <b>SHA-256 Cryptographic Custody:</b> Calculates immutable hashes upon file receipt to guarantee digital chain-of-custody.",
        bullet_style
    ))

    story.append(Paragraph("<b>B. Structured Forensic Intelligence via Gemini AI</b>", h2_style))
    story.append(Paragraph(
        "• <b>Objective Threat Scoring:</b> Computes calibrated risk scores (0–100) and severity tiers (LOW, MEDIUM, HIGH, CRITICAL).<br/>"
        "• <b>Entity Extraction:</b> Isolates phone numbers, UPI payment addresses (@okaxis, @ybl), bank accounts, person names, and URLs.<br/>"
        "• <b>Crime Pattern Classification:</b> Matches patterns against known fraud types (Fake KYC Expiration, Police Impersonation, UPI Scams).<br/>"
        "• <b>Suspicious Indicators:</b> Detects coercion, false urgency, threats of account blockage, and credential harvesting tactics.",
        bullet_style
    ))

    story.append(Paragraph("<b>C. Cross-Case Entity Correlation & Serial Ring Detection</b>", h2_style))
    story.append(Paragraph(
        "• The system continuously cross-references extracted phone numbers, UPI addresses, and bank accounts across all cases.<br/>"
        "• When an entity appears in two or more distinct cases, it is elevated to <b>'Flagged (Multi-Evidence)'</b> status, "
        "enabling investigators to identify organized crime syndicates operating across different victims.",
        body_style
    ))

    # Section 5: Database Schema
    story.append(Paragraph("5. Relational Database Schema (crime_investigator.db)", h1_style))
    
    schema_data = [
        [Paragraph("Table", table_header_style), Paragraph("Key Columns", table_header_style), Paragraph("Relationships & Constraints", table_header_style)],
        [
            Paragraph("<b>users</b>", table_cell_bold),
            Paragraph("id (PK), name, email (UNIQUE), password (HASH), created_at", table_cell_style),
            Paragraph("Has many Cases. Cascade deletes all related investigation records.", table_cell_style)
        ],
        [
            Paragraph("<b>cases</b>", table_cell_bold),
            Paragraph("id (PK), title, description, status, user_id (FK), created_at", table_cell_style),
            Paragraph("Belongs to User. Has many Evidence items, Analyses, and Reports.", table_cell_style)
        ],
        [
            Paragraph("<b>evidence</b>", table_cell_bold),
            Paragraph("id (PK), filename, stored_filename, filepath, file_type, size_bytes, sha256_hash, extracted_text, case_id (FK), uploaded_at", table_cell_style),
            Paragraph("Belongs to Case. Stores digital fingerprint and raw extracted text content.", table_cell_style)
        ],
        [
            Paragraph("<b>analyses</b>", table_cell_bold),
            Paragraph("id (PK), case_id (FK), evidence_id (FK), result_json, risk_level, risk_score, analyzed_at", table_cell_style),
            Paragraph("Stores raw structured AI JSON, risk metrics, and timestamps.", table_cell_style)
        ],
        [
            Paragraph("<b>reports</b>", table_cell_bold),
            Paragraph("id (PK), case_id (FK), filename, filepath, generated_at", table_cell_style),
            Paragraph("Tracks finalized court-ready PDF documents generated on the server.", table_cell_style)
        ]
    ]
    t_schema = Table(schema_data, colWidths=[70, 220, 214])
    t_schema.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 10))

    # Section 6: File & Directory Manifest
    story.append(Paragraph("6. Project Structure & Module Manifest", h1_style))

    manifest_text = (
        "C:\\gg\\AI-Digital-Crime-Investigator\\\n"
        "├── ai-module/              [AI Microservice - Port 5001]\n"
        "│   ├── app.py              - Microservice HTTP server & /analyze endpoint\n"
        "│   ├── analyzer.py         - Gemini model router, prompt logic & regex fallback\n"
        "│   ├── entities.py         - Cross-evidence relationship evaluator\n"
        "│   ├── timeline.py         - Chronological event organizer\n"
        "│   ├── ocr.py              - Tesseract OCR wrapper for images\n"
        "│   ├── speech.py           - Whisper STT voice transcription\n"
        "│   └── .env                - Gemini API credentials\n"
        "├── backend/                [Flask REST Backend - Port 5000]\n"
        "│   ├── app.py              - Server entry, CORS, and Blueprint registration\n"
        "│   ├── config.py           - Paths, database config, and JWT parameters\n"
        "│   ├── models.py           - SQLAlchemy 2.0 ORM database schema\n"
        "│   ├── database.py         - SQLAlchemy engine instance\n"
        "│   ├── routes/             - auth.py, cases.py, evidence.py, analysis.py, entities.py, reports.py\n"
        "│   ├── uploads/            - Ingested evidence disk repository\n"
        "│   └── reports/            - Generated forensic PDF document storage\n"
        "├── frontend/               [React 19 Single Page App - Port 5173]\n"
        "│   ├── src/pages/          - Dashboard.jsx, Entities.jsx, Timeline.jsx, Reports.jsx, login.jsx, Signup.jsx\n"
        "│   ├── src/components/     - Navbar, Sidebar, Hero, Workflow, Features, Scenarios, SecurityBanner\n"
        "│   ├── src/context/        - AuthContext.jsx session provider\n"
        "│   └── vite.config.js      - Vite proxy configuration\n"
        "└── run_all.bat             - Master launch automation script"
    )
    
    t_manifest = Table([[Paragraph(f"<pre>{manifest_text}</pre>", code_style)]], colWidths=[504])
    t_manifest.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_manifest)
    story.append(Spacer(1, 10))

    # Section 7: Operations & Quickstart
    story.append(Paragraph("7. Launch & Execution Procedures", h1_style))
    story.append(Paragraph(
        "<b>Single-Command Launcher:</b> Execute <code>run_all.bat</code> from the root directory. "
        "This triggers <code>start_ai_module.bat</code>, <code>start_backend.bat</code>, and <code>start_frontend.bat</code> in sequence.<br/>"
        "<b>Access Endpoint:</b> Open <b>http://localhost:5173</b> in any modern web browser to access the investigator console.",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build completed:", output_path)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "AIDCI_Project_Overview.pdf"
    build_pdf(out)

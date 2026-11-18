from datetime import datetime
from database import db
from sqlalchemy.orm import relationship


# ============================================================
# USER MODEL
# ============================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    cases = relationship("Case", back_populates="user", cascade="all, delete-orphan")


# ============================================================
# CASE MODEL
# ============================================================

class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="open", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    user = relationship("User", back_populates="cases")
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")


# ============================================================
# EVIDENCE MODEL
# ============================================================

class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=True)
    filepath = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)
    sha256_hash = db.Column(db.String(64), nullable=True, index=True)
    extracted_text = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False,
        index=True
    )

    case = relationship("Case", back_populates="evidence")
    analyses = relationship("Analysis", back_populates="evidence", cascade="all, delete-orphan")


# ============================================================
# ANALYSIS MODEL
# ============================================================

class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False,
        index=True
    )
    evidence_id = db.Column(
        db.Integer,
        db.ForeignKey("evidence.id"),
        nullable=True,
        index=True
    )
    result_json = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(30), nullable=True)
    risk_score = db.Column(db.Integer, default=0)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="analyses")
    evidence = relationship("Evidence", back_populates="analyses")


# ============================================================
# REPORT MODEL
# ============================================================

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False,
        index=True
    )
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="reports")

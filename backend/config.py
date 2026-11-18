import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "crime_investigator.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "my-secret-key-digital-forensics-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "my-jwt-secret-key-digital-forensics-2026")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
    AI_MODULE_URL = os.getenv("AI_MODULE_URL", "http://127.0.0.1:5001/analyze")

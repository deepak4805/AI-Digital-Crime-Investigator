import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db
from models import User, Case, Evidence, Analysis, Report

from routes.auth import auth_bp
from routes.cases import cases_bp
from routes.evidence import evidence_bp
from routes.analysis import analysis_bp
from routes.entities import entities_bp
from routes.reports import reports_bp

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all frontend routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

jwt = JWTManager(app)
db.init_app(app)

# Register all Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(cases_bp)
app.register_blueprint(evidence_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(entities_bp)
app.register_blueprint(reports_bp)

# Auto create tables
with app.app_context():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)
    db.create_all()


@app.route("/")
def home():
    return "AI Digital Crime Investigator Backend API is running!"


@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "service": "AIDCI Backend",
        "database": "connected"
    }), 200


if __name__ == "__main__":
    print("==================================================")
    print(" AI DIGITAL CRIME INVESTIGATOR - BACKEND (Flask)")
    print(" Server running on http://127.0.0.1:5000")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)

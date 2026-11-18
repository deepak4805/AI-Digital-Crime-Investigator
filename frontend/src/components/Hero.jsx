import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Hero() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleStart = () => {
    navigate(isAuthenticated ? "/dashboard" : "/signup");
  };

  return (
    <section className="hero-section">
      <div className="hero-container">
        {/* Left: Simple Headline & Action */}
        <div className="hero-copy">
          <div className="hero-pill">
            <span>✨ AI-Powered Cyber Crime Investigation</span>
          </div>

          <h1 className="hero-headline">
            Investigate Digital Crimes <span className="highlight-text">Easily with AI</span>
          </h1>

          <p className="hero-subtitle">
            Upload screenshots, messages, or files. Our AI automatically extracts the text, detects scams, finds connected clues, and creates an official PDF investigation report in seconds.
          </p>

          <div className="hero-cta-group">
            <button className="primary-hero-btn" onClick={handleStart}>
              🚀 Start Investigation Now
            </button>
            <a href="#how-it-works" className="secondary-hero-btn">
              See How It Works ↓
            </a>
          </div>

          {/* Key Simple Benefits */}
          <div className="hero-quick-points">
            <div className="quick-point">
              <span className="check-icon">✔</span> No manual typing (Auto OCR)
            </div>
            <div className="quick-point">
              <span className="check-icon">✔</span> Smart Gemini AI Analysis
            </div>
            <div className="quick-point">
              <span className="check-icon">✔</span> One-Click PDF Report
            </div>
          </div>
        </div>

        {/* Right: Simple Live Demo Card */}
        <div className="hero-card-wrapper">
          <div className="demo-card">
            <div className="demo-card-header">
              <span className="demo-badge">LIVE EXAMPLE</span>
              <span className="demo-status">● Instant Detection</span>
            </div>

            {/* Step 1: Input */}
            <div className="demo-section">
              <span className="demo-label">1. SUSPICIOUS MESSAGE RECEIVED:</span>
              <div className="demo-message-box">
                "URGENT: Your Bank account is BLOCKED due to expired KYC. Transfer ₹5,000 to <b>fraud@upi</b> immediately or face police action. Contact +91 98765 43210."
              </div>
            </div>

            {/* Arrow Divider */}
            <div className="demo-arrow">
              <span>⚡ AI SCANS EVIDENCE ➔</span>
            </div>

            {/* Step 2: Output */}
            <div className="demo-section">
              <span className="demo-label">2. WHAT AI FINDS INSTANTLY:</span>
              <div className="demo-results-box">
                <div className="result-row">
                  <span className="res-title">🚨 Threat Level:</span>
                  <span className="risk-tag-high">HIGH RISK (85%)</span>
                </div>
                <div className="result-row">
                  <span className="res-title">🕵️ Crime Type:</span>
                  <span className="res-value">Fake KYC & UPI Extortion</span>
                </div>
                <div className="result-row">
                  <span className="res-title">💳 Flagged UPI ID:</span>
                  <span className="res-value code-val">fraud@upi</span>
                </div>
                <div className="result-row">
                  <span className="res-title">📞 Suspect Phone:</span>
                  <span className="res-value code-val">+91 98765 43210</span>
                </div>
                <div className="result-row">
                  <span className="res-title">💰 Demanded Amount:</span>
                  <span className="res-value code-val">₹5,000</span>
                </div>
              </div>
            </div>

            {/* Step 3: Action */}
            <div className="demo-footer">
              <button className="demo-pdf-btn" onClick={handleStart}>
                📄 Download Official PDF Report →
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;

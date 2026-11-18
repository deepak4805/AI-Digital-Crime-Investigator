import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "radial-gradient(circle at top, #1e293b 0%, #090d16 100%)",
        padding: "24px",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "#111827",
          border: "1px solid #1f2937",
          borderRadius: "16px",
          padding: "36px 32px",
          boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
        }}
      >
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "56px",
              height: "56px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
              fontSize: "26px",
              marginBottom: "14px",
              boxShadow: "0 8px 16px rgba(2,132,199,0.3)",
            }}
          >
            🛡️
          </div>
          <h1 style={{ fontSize: "22px", fontWeight: 700, margin: "0 0 6px 0", color: "#f8fafc" }}>
            Investigator Access
          </h1>
          <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
            Sign in to AI Digital Crime Investigator
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div
            style={{
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid #ef4444",
              color: "#fca5a5",
              padding: "12px 14px",
              borderRadius: "8px",
              fontSize: "13px",
              marginBottom: "20px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
              Investigator Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="agent@forensics.org"
              required
              style={{
                width: "100%",
                padding: "12px 14px",
                background: "#0b0f19",
                border: "1px solid #334155",
                borderRadius: "8px",
                color: "#f8fafc",
                fontSize: "14px",
                outline: "none",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "#cbd5e1", marginBottom: "6px" }}>
              Security Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              style={{
                width: "100%",
                padding: "12px 14px",
                background: "#0b0f19",
                border: "1px solid #334155",
                borderRadius: "8px",
                color: "#f8fafc",
                fontSize: "14px",
                outline: "none",
                boxSizing: "border-box",
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: "8px",
              padding: "13px",
              background: loading ? "#0369a1" : "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
              boxShadow: "0 4px 12px rgba(2,132,199,0.3)",
            }}
          >
            {loading ? "Authenticating..." : "Sign In to Workspace"}
          </button>
        </form>

        {/* Footer Link */}
        <div style={{ marginTop: "24px", textAlign: "center", fontSize: "13px", color: "#94a3b8" }}>
          Don't have an account?{" "}
          <Link to="/signup" style={{ color: "#38bdf8", textDecoration: "none", fontWeight: 600 }}>
            Sign Up
          </Link>
        </div>

        <div style={{ marginTop: "16px", textAlign: "center", fontSize: "12px" }}>
          <Link to="/" style={{ color: "#64748b", textDecoration: "none" }}>
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;

import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

function formatSize(bytes) {
  if (!bytes && bytes !== 0) return "Unknown size";
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function Dashboard() {
  const { authFetch, API_BASE } = useAuth();

  // Cases state
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);
  const [newCaseTitle, setNewCaseTitle] = useState("");
  const [newCaseDesc, setNewCaseDesc] = useState("");

  // Evidence & Analysis state
  const [uploadedEvidence, setUploadedEvidence] = useState(null);
  const [evidenceText, setEvidenceText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Load cases on mount
  useEffect(() => {
    fetchCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchCases() {
    try {
      const res = await authFetch("/api/cases/");
      if (res.ok) {
        const data = await res.json();
        setCases(data.cases || []);
        if (data.cases && data.cases.length > 0 && !selectedCaseId) {
          setSelectedCaseId(String(data.cases[0].id));
        }
      }
    } catch (err) {
      console.error("Fetch cases error:", err);
    }
  }

  async function handleCreateCase(e) {
    e.preventDefault();
    if (!newCaseTitle.trim()) return;

    try {
      const res = await authFetch("/api/cases/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newCaseTitle,
          description: newCaseDesc,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to create case");

      setShowNewCaseModal(false);
      setNewCaseTitle("");
      setNewCaseDesc("");
      setSuccessMsg(`Case #${data.case.id} "${data.case.title}" created!`);
      await fetchCases();
      setSelectedCaseId(String(data.case.id));
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // file selected
    setError(null);
    setAnalysis(null);

    // If a case is selected, automatically upload and run OCR/extraction
    if (!selectedCaseId) {
      setError("Please select or create a case before uploading evidence.");
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      const res = await authFetch(`/api/cases/${selectedCaseId}/evidence/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Upload failed");

      setUploadedEvidence(data.evidence);
      setSuccessMsg(`Evidence "${file.name}" uploaded (SHA-256: ${data.evidence.sha256_hash?.slice(0, 12)}...)`);

      if (data.evidence.extracted_text) {
        setEvidenceText(data.evidence.extracted_text);
      } else if (file.type.startsWith("text/")) {
        const reader = new FileReader();
        reader.onload = (e) => setEvidenceText(e.target.result || "");
        reader.readAsText(file);
      } else {
        setEvidenceText(`Evidence File: ${file.name}\nSize: ${formatSize(file.size)}\nHash: ${data.evidence.sha256_hash}`);
      }
    } catch (err) {
      setError(err.message || "Could not upload file.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAnalyze() {
    if (!evidenceText.trim()) {
      setError("Please enter or upload evidence text first.");
      return;
    }

    try {
      setAnalyzing(true);
      setError(null);
      setAnalysis(null);

      const res = await authFetch("/api/analysis/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: evidenceText,
          case_id: selectedCaseId ? parseInt(selectedCaseId) : null,
          evidence_id: uploadedEvidence ? uploadedEvidence.id : null,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.message || "Analysis failed");
      }

      setAnalysis(data.result);
      setSuccessMsg("AI forensic analysis completed successfully!");
      fetchCases(); // Refresh case list stats
    } catch (err) {
      console.error("Analysis error:", err);
      setError(err.message || "Could not connect to backend.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleGenerateReport() {
    if (!selectedCaseId) {
      setError("Please select a case to generate a report.");
      return;
    }

    try {
      setGeneratingReport(true);
      setError(null);

      const res = await authFetch("/api/report/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: parseInt(selectedCaseId) }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Report generation failed");

      if (data.download_url) {
        window.open(`${API_BASE}${data.download_url}`, "_blank");
      }
      setSuccessMsg("Investigation Report PDF generated and opened!");
    } catch (err) {
      setError(err.message || "Failed to generate report.");
    } finally {
      setGeneratingReport(false);
    }
  }

  function clearAnalysis() {
    // cleared
    setUploadedEvidence(null);
    setEvidenceText("");
    setAnalysis(null);
    setError(null);
    setSuccessMsg(null);
  }

  return (
    <div className="dashboard-layout">
      <Sidebar active="overview" />

      <main className="dashboard-main">
        {/* Header */}
        <header className="dashboard-header">
          <div>
            <p className="dashboard-label">AIDCI INVESTIGATION WORKSPACE</p>
            <h1>Investigator Dashboard</h1>
            <p>Securely ingest digital evidence, extract OCR text, and analyze with Gemini AI.</p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              className="new-case-btn"
              onClick={() => setShowNewCaseModal(true)}
              style={{ background: "#0284c7", color: "#fff", border: "none", padding: "10px 18px", borderRadius: "8px", cursor: "pointer", fontWeight: 600 }}
            >
              + Create Case
            </button>
            <button
              className="new-case-btn"
              onClick={clearAnalysis}
              style={{ background: "#334155", color: "#fff", border: "none", padding: "10px 18px", borderRadius: "8px", cursor: "pointer" }}
            >
              Reset View
            </button>
          </div>
        </header>

        {/* Case Selector Bar */}
        <section
          style={{
            background: "#111827",
            border: "1px solid #1f2937",
            borderRadius: "12px",
            padding: "16px 20px",
            marginBottom: "24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "14px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "18px" }}>📁</span>
            <div>
              <div style={{ fontSize: "12px", color: "#94a3b8", fontWeight: 600 }}>ACTIVE CASE</div>
              <select
                value={selectedCaseId}
                onChange={(e) => setSelectedCaseId(e.target.value)}
                style={{
                  background: "#0b0f19",
                  color: "#f8fafc",
                  border: "1px solid #334155",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  fontSize: "14px",
                  marginTop: "4px",
                  outline: "none",
                }}
              >
                {cases.length === 0 ? (
                  <option value="">No cases created yet</option>
                ) : (
                  cases.map((c) => (
                    <option key={c.id} value={c.id}>
                      Case #{c.id}: {c.title} ({c.evidence_count || 0} files)
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {selectedCaseId && (
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              style={{
                background: "linear-gradient(135deg, #059669 0%, #047857 100%)",
                color: "#fff",
                border: "none",
                padding: "10px 18px",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: 600,
                cursor: generatingReport ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              📄 {generatingReport ? "Generating PDF..." : "Export Formal PDF Report"}
            </button>
          )}
        </section>

        {/* Notifications */}
        {error && (
          <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "12px 16px", borderRadius: "8px", marginBottom: "20px" }}>
            ⚠️ {error}
          </div>
        )}

        {successMsg && (
          <div style={{ background: "rgba(16, 185, 129, 0.15)", border: "1px solid #10b981", color: "#6ee7b7", padding: "12px 16px", borderRadius: "8px", marginBottom: "20px" }}>
            ✅ {successMsg}
          </div>
        )}

        {/* Statistics Cards */}
        <section className="stats-grid">
          <div className="stat-card">
            <span>📁</span>
            <h3>Evidence Items</h3>
            <strong>{uploadedEvidence ? "1" : "0"}</strong>
          </div>
          <div className="stat-card">
            <span>🔍</span>
            <h3>AI Status</h3>
            <strong>{analysis ? "Analyzed" : "Idle"}</strong>
          </div>
          <div className="stat-card">
            <span>⚠️</span>
            <h3>Risk Score</h3>
            <strong>{analysis?.risk_score ?? "-"}</strong>
          </div>
          <div className="stat-card">
            <span>🚨</span>
            <h3>Risk Level</h3>
            <strong style={{ color: analysis?.risk_level === "CRITICAL" ? "#ef4444" : analysis?.risk_level === "HIGH" ? "#f97316" : "#10b981" }}>
              {analysis?.risk_level ? String(analysis.risk_level).toUpperCase() : "-"}
            </strong>
          </div>
        </section>

        {/* Evidence Input & Processing */}
        <section className="dashboard-panel">
          <div style={{ width: "100%" }}>
            <p className="panel-label">EVIDENCE INGESTION & OCR</p>
            <h2>Process Digital Evidence</h2>
            <p>Upload screenshots, PDFs, logs, or paste suspicious communications for AI analysis.</p>

            {/* Textarea */}
            <textarea
              value={evidenceText}
              onChange={(e) => setEvidenceText(e.target.value)}
              placeholder="Paste suspicious messages, KYC scam texts, email headers, or transaction messages..."
              rows={7}
              style={{
                width: "100%",
                marginTop: "16px",
                padding: "16px",
                borderRadius: "10px",
                border: "1px solid #334155",
                background: "#0b0f19",
                color: "#f8fafc",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />

            {/* Buttons */}
            <div style={{ display: "flex", gap: "12px", marginTop: "16px", flexWrap: "wrap" }}>
              <label
                style={{
                  background: "#1e293b",
                  border: "1px solid #334155",
                  color: "#cbd5e1",
                  padding: "10px 18px",
                  borderRadius: "8px",
                  cursor: uploading ? "not-allowed" : "pointer",
                  fontWeight: 600,
                  fontSize: "14px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                📁 {uploading ? "Uploading & Running OCR..." : "Choose Evidence File (Image / PDF / Audio / Text)"}
                <input type="file" hidden disabled={uploading || analyzing} onChange={handleFileSelect} />
              </label>

              <button
                onClick={handleAnalyze}
                disabled={analyzing || uploading}
                style={{
                  background: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
                  color: "#fff",
                  border: "none",
                  padding: "10px 22px",
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: analyzing ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                {analyzing ? "⏳ Analyzing with Gemini..." : "🧠 Analyze with Gemini AI"}
              </button>

              {(evidenceText || analysis) && (
                <button
                  onClick={clearAnalysis}
                  style={{
                    background: "transparent",
                    border: "1px solid #475569",
                    color: "#94a3b8",
                    padding: "10px 16px",
                    borderRadius: "8px",
                    cursor: "pointer",
                  }}
                >
                  ✕ Clear
                </button>
              )}
            </div>

            {/* Uploaded File Meta */}
            {uploadedEvidence && (
              <div style={{ marginTop: "16px", padding: "14px 18px", borderRadius: "8px", background: "#0b0f19", border: "1px solid #1e293b" }}>
                <div style={{ color: "#38bdf8", fontWeight: 600 }}>📄 {uploadedEvidence.filename}</div>
                <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>
                  Size: {formatSize(uploadedEvidence.size_bytes)} • SHA-256 Hash: <code>{uploadedEvidence.sha256_hash}</code>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* AI Analysis Findings Display */}
        {analysis && (
          <section className="analysis-panel" style={{ marginTop: "24px" }}>
            <div className="analysis-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p className="panel-label">AI INVESTIGATION FINDINGS</p>
                <h2>Forensic Evaluation & Extracted Intelligence</h2>
              </div>
              <button
                onClick={() => setAnalysis(null)}
                style={{ background: "transparent", border: "none", color: "#94a3b8", fontSize: "18px", cursor: "pointer" }}
              >
                ✕
              </button>
            </div>

            {/* Metric Cards */}
            <div className="analysis-grid" style={{ marginTop: "16px" }}>
              <div className="analysis-card">
                <span>⚠️</span>
                <h3>Risk Score</h3>
                <p style={{ fontSize: "20px", fontWeight: 700 }}>{analysis.risk_score} / 100</p>
              </div>

              <div className="analysis-card">
                <span>🚨</span>
                <h3>Risk Level</h3>
                <p style={{ fontSize: "18px", fontWeight: 700, color: analysis.risk_level === "CRITICAL" ? "#ef4444" : "#f97316" }}>
                  {analysis.risk_level}
                </p>
              </div>

              <div className="analysis-card">
                <span>🚩</span>
                <h3>Suspicious Indicators</h3>
                <p>{Array.isArray(analysis.suspicious_indicators) ? analysis.suspicious_indicators.length : 0}</p>
              </div>

              <div className="analysis-card">
                <span>🕵️</span>
                <h3>Crime Patterns</h3>
                <p>{Array.isArray(analysis.crime_patterns) ? analysis.crime_patterns.length : 0}</p>
              </div>
            </div>

            {/* Executive Summary */}
            {analysis.summary && (
              <div className="analysis-card" style={{ marginTop: "16px" }}>
                <span>📝</span>
                <h3>Executive Summary</h3>
                <p>{analysis.summary}</p>
              </div>
            )}

            {/* Risk Reason */}
            {analysis.risk_reason && (
              <div className="analysis-card" style={{ marginTop: "16px" }}>
                <span>🛡️</span>
                <h3>Risk Rationale</h3>
                <p>{analysis.risk_reason}</p>
              </div>
            )}

            {/* Indicators */}
            {analysis.suspicious_indicators?.length > 0 && (
              <div className="analysis-card" style={{ marginTop: "16px" }}>
                <span>🚩</span>
                <h3>Flagged Indicators</h3>
                <ul>
                  {analysis.suspicious_indicators.map((ind, i) => (
                    <li key={i} style={{ color: "#fca5a5", marginBottom: "4px" }}>• {String(ind)}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Patterns */}
            {analysis.crime_patterns?.length > 0 && (
              <div className="analysis-card" style={{ marginTop: "16px" }}>
                <span>🕵️</span>
                <h3>Crime Patterns Detected</h3>
                <ul>
                  {analysis.crime_patterns.map((pat, i) => (
                    <li key={i} style={{ color: "#fed7aa", marginBottom: "4px" }}>• {String(pat)}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Financials & Phone Numbers */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px", marginTop: "16px" }}>
              {analysis.amounts?.length > 0 && (
                <div className="analysis-card">
                  <span>💰</span>
                  <h3>Amounts Mentioned</h3>
                  <p>{analysis.amounts.join(", ")}</p>
                </div>
              )}
              {analysis.upi_ids?.length > 0 && (
                <div className="analysis-card">
                  <span>💳</span>
                  <h3>UPI IDs</h3>
                  <p>{analysis.upi_ids.join(", ")}</p>
                </div>
              )}
              {analysis.phone_numbers?.length > 0 && (
                <div className="analysis-card">
                  <span>📞</span>
                  <h3>Phone Numbers</h3>
                  <p>{analysis.phone_numbers.join(", ")}</p>
                </div>
              )}
              {analysis.urls?.length > 0 && (
                <div className="analysis-card">
                  <span>🔗</span>
                  <h3>URLs</h3>
                  <p>{analysis.urls.join(", ")}</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* New Case Modal */}
        {showNewCaseModal && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.75)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
              padding: "16px",
            }}
          >
            <div
              style={{
                width: "100%",
                maxWidth: "460px",
                background: "#111827",
                border: "1px solid #1f2937",
                borderRadius: "16px",
                padding: "28px",
                boxShadow: "0 20px 40px rgba(0,0,0,0.8)",
              }}
            >
              <h2 style={{ margin: "0 0 12px 0", fontSize: "18px", color: "#f8fafc" }}>
                Create New Investigation Case
              </h2>
              <form onSubmit={handleCreateCase} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "6px" }}>
                    Case Title / Reference *
                  </label>
                  <input
                    type="text"
                    value={newCaseTitle}
                    onChange={(e) => setNewCaseTitle(e.target.value)}
                    placeholder="e.g. Operation Fake KYC Bank Scam"
                    required
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      background: "#0b0f19",
                      border: "1px solid #334155",
                      borderRadius: "6px",
                      color: "#f8fafc",
                      boxSizing: "border-box",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "6px" }}>
                    Case Description
                  </label>
                  <textarea
                    value={newCaseDesc}
                    onChange={(e) => setNewCaseDesc(e.target.value)}
                    placeholder="Brief background on reported victim or incident..."
                    rows={3}
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      background: "#0b0f19",
                      border: "1px solid #334155",
                      borderRadius: "6px",
                      color: "#f8fafc",
                      boxSizing: "border-box",
                    }}
                  />
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "10px" }}>
                  <button
                    type="button"
                    onClick={() => setShowNewCaseModal(false)}
                    style={{ background: "transparent", border: "1px solid #475569", color: "#cbd5e1", padding: "8px 16px", borderRadius: "6px", cursor: "pointer" }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{ background: "#0284c7", color: "#fff", border: "none", padding: "8px 18px", borderRadius: "6px", fontWeight: 600, cursor: "pointer" }}
                  >
                    Save Case
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;

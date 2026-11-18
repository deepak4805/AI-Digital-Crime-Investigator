import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

function formatDateTime(isoString) {
  if (!isoString) return "Unknown date";
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Reports() {
  const { authFetch, API_BASE } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  async function fetchReports() {
    try {
      const res = await authFetch("/api/reports");
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const data = await res.json();
      setReports(data.reports || []);
    } catch (err) {
      console.error("Reports fetch error:", err);
      setError("Could not load reports from backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let ignore = false;
    async function loadReports() {
      try {
        const res = await authFetch("/api/reports");
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        const data = await res.json();
        if (!ignore) {
          setReports(data.reports || []);
        }
      } catch (err) {
        if (!ignore) {
          console.error("Reports fetch error:", err);
          setError("Could not load reports from backend.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadReports();
    return () => {
      ignore = true;
    };
  }, [authFetch]);

  async function handleGenerateReport() {
    try {
      setGenerating(true);
      setError(null);
      setSuccessMsg(null);

      const res = await authFetch("/api/report/generate", {
        method: "POST",
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to generate report");

      setSuccessMsg("Investigation Report PDF generated successfully!");
      if (data.download_url) {
        window.open(`${API_BASE}${data.download_url}`, "_blank");
      }
      await fetchReports();
    } catch (err) {
      setError(err.message || "Failed to generate report.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDeleteReport(reportId) {
    try {
      const res = await authFetch(`/api/reports/${reportId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Delete failed");

      setReports((prev) => prev.filter((r) => r.id !== reportId));
      setSuccessMsg("Report deleted.");
    } catch (err) {
      setError(err.message || "Could not delete report.");
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar active="reports" />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-label">AIDCI INVESTIGATION WORKSPACE</p>
            <h1>Investigation Reports</h1>
            <p>Formal PDF investigation reports with evidence chains, risk assessments, and OCR transcripts.</p>
          </div>

          <button
            className="new-case-btn"
            disabled={generating}
            onClick={handleGenerateReport}
            style={{
              background: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
              color: "#fff",
              border: "none",
              padding: "10px 20px",
              borderRadius: "8px",
              fontWeight: 600,
              cursor: generating ? "not-allowed" : "pointer",
            }}
          >
            {generating ? "⏳ Generating PDF..." : "📄 Generate PDF Report"}
          </button>
        </header>

        {error && (
          <div style={{ background: "rgba(239,68,68,0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "12px 16px", borderRadius: "8px", marginBottom: "24px" }}>
            ⚠️ {error}
          </div>
        )}

        {successMsg && (
          <div style={{ background: "rgba(16,185,129,0.15)", border: "1px solid #10b981", color: "#6ee7b7", padding: "12px 16px", borderRadius: "8px", marginBottom: "24px" }}>
            ✅ {successMsg}
          </div>
        )}

        <section className="evidence-section">
          <div className="evidence-section-header">
            <div>
              <p className="panel-label">DOCUMENT REPOSITORY</p>
              <h2>Generated PDF Reports</h2>
            </div>
            <div className="evidence-count">
              {reports.length} {reports.length === 1 ? "REPORT" : "REPORTS"}
            </div>
          </div>

          {loading ? (
            <p style={{ color: "#94a3b8" }}>Loading reports...</p>
          ) : reports.length === 0 ? (
            <div className="analysis-placeholder">
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>📄</div>
              <h3>No investigation reports generated yet</h3>
              <p>Click "Generate PDF Report" to compile all case findings into a formal forensic document.</p>
            </div>
          ) : (
            <div className="evidence-list">
              {reports.map((report) => (
                <div className="evidence-card" key={report.id}>
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <h3>{report.filename}</h3>
                    <div className="file-meta">
                      <span>Case #{report.case_id}</span>
                      <span>•</span>
                      <span>Generated {formatDateTime(report.generated_at)}</span>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    {report.download_url && (
                      <a
                        href={`${API_BASE}${report.download_url}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          background: "#0284c7",
                          color: "#fff",
                          padding: "8px 14px",
                          borderRadius: "6px",
                          textDecoration: "none",
                          fontSize: "13px",
                          fontWeight: 600,
                        }}
                      >
                        📥 Download / View PDF
                      </a>
                    )}
                    <button
                      onClick={() => handleDeleteReport(report.id)}
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "#ef4444",
                        fontSize: "16px",
                        cursor: "pointer",
                        padding: "8px",
                      }}
                      title="Delete Report"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Reports;

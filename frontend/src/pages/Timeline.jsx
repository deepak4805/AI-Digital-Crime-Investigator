import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

function formatSize(bytes) {
  if (!bytes && bytes !== 0) return "Unknown size";
  return `${(bytes / 1024).toFixed(1)} KB`;
}

function formatDateTime(isoString) {
  if (!isoString) return "Unknown date";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "Unknown date";
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Timeline() {
  const { authFetch } = useAuth();
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    async function loadTimeline() {
      try {
        const res = await authFetch("/api/evidence");
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        const data = await res.json();
        if (!ignore) {
          setEvidenceList(data.evidence || []);
        }
      } catch (err) {
        if (!ignore) {
          console.error("Timeline error:", err);
          setError("Could not load timeline evidence.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadTimeline();
    return () => {
      ignore = true;
    };
  }, [authFetch]);

  return (
    <div className="dashboard-layout">
      <Sidebar active="timeline" />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-label">AIDCI INVESTIGATION WORKSPACE</p>
            <h1>Investigation Timeline</h1>
            <p>Chronological evidence chain of custody and forensic ingestion timestamps.</p>
          </div>
        </header>

        {error && (
          <div style={{ background: "rgba(239,68,68,0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "12px 16px", borderRadius: "8px", marginBottom: "24px" }}>
            ⚠️ {error}
          </div>
        )}

        {loading ? (
          <p style={{ color: "#94a3b8" }}>Loading investigation timeline...</p>
        ) : evidenceList.length === 0 ? (
          <div className="analysis-placeholder">
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>⏱️</div>
            <h3>No evidence items on timeline</h3>
            <p>Upload digital evidence from the dashboard to populate the chronological timeline.</p>
          </div>
        ) : (
          <div style={{ position: "relative", paddingLeft: "32px", borderLeft: "2px solid #334155", margin: "20px 0 0 10px" }}>
            {evidenceList.map((item) => (
              <div key={item.id} style={{ position: "relative", marginBottom: "32px" }}>
                {/* Node Dot */}
                <div
                  style={{
                    position: "absolute",
                    left: "-39px",
                    top: "4px",
                    width: "14px",
                    height: "14px",
                    borderRadius: "50%",
                    background: "#0284c7",
                    boxShadow: "0 0 0 4px rgba(2,132,199,0.3)",
                  }}
                />

                <p style={{ fontSize: "12px", color: "#38bdf8", fontWeight: 600, margin: "0 0 6px 0" }}>
                  {formatDateTime(item.uploaded_at)}
                </p>

                <div className="evidence-card" style={{ maxWidth: "620px" }}>
                  <div className="file-icon">📄</div>
                  <div className="file-info">
                    <h3>{item.filename}</h3>
                    <div className="file-meta">
                      <span>{formatSize(item.size_bytes)}</span>
                      <span>•</span>
                      <span>Case #{item.case_id}</span>
                      <span>•</span>
                      <span>SHA-256: <code>{item.sha256_hash ? item.sha256_hash.slice(0, 16) + "..." : "N/A"}</code></span>
                    </div>
                    {item.extracted_text && (
                      <div style={{ marginTop: "8px", fontSize: "12px", color: "#94a3b8", fontStyle: "italic" }}>
                        "{item.extracted_text.slice(0, 140)}..."
                      </div>
                    )}
                  </div>
                  <div className="file-status">
                    <span className="status-dot"></span>
                    Evidence #{item.id}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Timeline;

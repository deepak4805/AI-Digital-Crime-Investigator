import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";

const TYPE_LABELS = {
  phone_numbers: { label: "Phone Number", icon: "📞" },
  urls: { label: "URL", icon: "🔗" },
  upi_ids: { label: "UPI ID", icon: "💳" },
  bank_accounts: { label: "Bank Account", icon: "🏦" },
  names: { label: "Person Name", icon: "👤" },
};

function Entities() {
  const { authFetch } = useAuth();
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    async function loadEntities() {
      try {
        const res = await authFetch("/api/entities/suspicious");
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        const data = await res.json();
        if (!ignore) {
          setEntities(data.suspicious_entities || []);
        }
      } catch (err) {
        if (!ignore) {
          console.error("Entities error:", err);
          setError("Could not load entities. Ensure backend is running.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadEntities();
    return () => {
      ignore = true;
    };
  }, [authFetch]);

  return (
    <div className="dashboard-layout">
      <Sidebar active="entities" />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-label">AIDCI INVESTIGATION WORKSPACE</p>
            <h1>Cross-Referenced Entities</h1>
            <p>
              Contacts, payment IDs, and links cross-referenced across analyzed evidence.
            </p>
          </div>
        </header>

        {error && (
          <div style={{ background: "rgba(239,68,68,0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "12px 16px", borderRadius: "8px", marginBottom: "24px" }}>
            ⚠️ {error}
          </div>
        )}

        <section className="evidence-section">
          <div className="evidence-section-header">
            <div>
              <p className="panel-label">DISCOVERED ARTIFACTS</p>
              <h2>Flagged & Repeated Entities</h2>
              <p>Entities linked to multiple evidence items are flagged with highest forensic priority.</p>
            </div>
            <div className="evidence-count">
              {entities.length} {entities.length === 1 ? "ENTITY" : "ENTITIES"}
            </div>
          </div>

          {loading ? (
            <p style={{ color: "#94a3b8" }}>Loading entity registry...</p>
          ) : entities.length === 0 ? (
            <div className="analysis-placeholder">
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>🔍</div>
              <h3>No entities found yet</h3>
              <p>Upload and analyze evidence in your cases to automatically extract and cross-reference suspicious entities.</p>
            </div>
          ) : (
            <div className="evidence-list">
              {entities.map((item, index) => {
                const info = TYPE_LABELS[item.type] || { label: item.type, icon: "❓" };
                return (
                  <div className="evidence-card" key={index}>
                    <div className="file-icon">{info.icon}</div>
                    <div className="file-info">
                      <h3>{item.value}</h3>
                      <div className="file-meta">
                        <span>{info.label}</span>
                        <span>•</span>
                        <span>Found in {item.count} {item.count === 1 ? "evidence" : "evidences"}</span>
                      </div>
                    </div>
                    <div className="file-status" style={{ color: item.is_flagged ? "#ef4444" : "#38bdf8" }}>
                      <span className="status-dot" style={{ background: item.is_flagged ? "#ef4444" : "#38bdf8" }}></span>
                      {item.is_flagged ? "Flagged (Multi-Evidence)" : "Observed"}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Entities;

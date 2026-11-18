import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Sidebar({ active }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = [
    { key: "overview", label: "📊 Overview", to: "/dashboard" },
    { key: "timeline", label: "⏱️ Timeline", to: "/dashboard/timeline" },
    { key: "entities", label: "⚠️ Entities", to: "/dashboard/entities" },
    { key: "reports", label: "📄 Reports", to: "/dashboard/reports" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span style={{ color: "#38bdf8" }}>🛡️</span> AIDCI
      </div>

      {user && (
        <div
          style={{
            padding: "10px 14px",
            background: "#1e293b",
            borderRadius: "8px",
            margin: "0 12px 16px 12px",
            fontSize: "12px",
            color: "#94a3b8",
          }}
        >
          <div style={{ color: "#f8fafc", fontWeight: 600 }}>{user.name}</div>
          <div style={{ fontSize: "11px", color: "#38bdf8" }}>Investigator Active</div>
        </div>
      )}

      <nav className="sidebar-nav">
        {links.map((link) => (
          <Link
            key={link.key}
            to={link.to}
            className={active === link.key ? "active" : ""}
          >
            {link.label}
          </Link>
        ))}
      </nav>

      <div className="sidebar-bottom" style={{ display: "flex", flexDirection: "column", gap: "10px", padding: "16px" }}>
        <Link to="/" style={{ color: "#94a3b8", textDecoration: "none", fontSize: "13px" }}>
          ← Back to Home
        </Link>
        <button
          onClick={() => {
            logout();
            navigate("/login");
          }}
          style={{
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid #ef4444",
            color: "#fca5a5",
            padding: "8px",
            borderRadius: "6px",
            fontSize: "12px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Sign Out
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;

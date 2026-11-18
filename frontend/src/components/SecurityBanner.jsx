import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function SecurityBanner() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <section className="cta-banner-section">
      <div className="cta-banner-box">
        <h2>Start Your Digital Crime Investigation Today</h2>
        <p>
          Create a free investigator account, upload evidence, and let AI do the heavy lifting.
        </p>
        <button
          className="cta-action-btn"
          onClick={() => navigate(isAuthenticated ? "/dashboard" : "/signup")}
        >
          🚀 Open Investigation Workspace
        </button>
      </div>
    </section>
  );
}

export default SecurityBanner;

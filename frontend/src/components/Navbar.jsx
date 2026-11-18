import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="navbar-wrapper">
      <nav className="navbar">
        <Link to="/" className="navbar-brand">
          <span className="logo-icon">🛡️</span>
          <span className="logo-title">AIDCI</span>
        </Link>

        <ul className="nav-links">
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#scams">What We Detect</a></li>
        </ul>

        <div className="navbar-actions">
          {isAuthenticated ? (
            <div className="user-nav-group">
              <span className="user-greeting">👤 {user?.name || "Investigator"}</span>
              <Link to="/dashboard" className="primary-nav-btn">
                Go to Workspace →
              </Link>
              <button onClick={logout} className="signout-btn">
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-nav-group">
              <Link to="/login" className="login-link-btn">
                Login
              </Link>
              <Link to="/signup" className="primary-nav-btn">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}

export default Navbar;

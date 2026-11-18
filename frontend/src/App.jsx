import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Workflow from "./components/Workflow";
import Features from "./components/Features";
import Scenarios from "./components/Scenarios";
import SecurityBanner from "./components/SecurityBanner";
import Footer from "./components/Footer.jsx";
import Login from "./pages/login.jsx";
import Signup from "./pages/Signup.jsx";
import Dashboard from "./pages/Dashboard";
import Entities from "./pages/Entities";
import Timeline from "./pages/Timeline";
import Reports from "./pages/Reports";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#090d16", color: "#f8fafc" }}>
        🛡️ Loading workspace...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function Home() {
  return (
    <div className="landing-page">
      <Navbar />
      <Hero />
      <Workflow />
      <Features />
      <Scenarios />
      <SecurityBanner />
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/entities"
            element={
              <ProtectedRoute>
                <Entities />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/timeline"
            element={
              <ProtectedRoute>
                <Timeline />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

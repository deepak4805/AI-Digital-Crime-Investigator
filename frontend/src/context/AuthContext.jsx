/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("aidci_token") || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("aidci_user");
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function verifySession() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data.user);
          localStorage.setItem("aidci_user", JSON.stringify(data.user));
        } else {
          logout();
        }
      } catch (err) {
        console.error("Session verification failed:", err);
      } finally {
        setLoading(false);
      }
    }
    verifySession();
  }, [token]);

  async function login(email, password) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || "Login failed");
    }

    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("aidci_token", data.access_token);
    localStorage.setItem("aidci_user", JSON.stringify(data.user));
    return data;
  }

  async function register(name, email, password) {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || "Registration failed");
    }

    if (data.access_token) {
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem("aidci_token", data.access_token);
      localStorage.setItem("aidci_user", JSON.stringify(data.user));
    }
    return data;
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("aidci_token");
    localStorage.removeItem("aidci_user");
  }

  async function authFetch(url, options = {}) {
    const headers = options.headers ? { ...options.headers } : {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(url.startsWith("http") ? url : `${API_BASE}${url}`, {
      ...options,
      headers,
    });
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated: !!token,
        login,
        register,
        logout,
        authFetch,
        API_BASE,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

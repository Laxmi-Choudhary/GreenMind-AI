// frontend/src/context/AuthContext.jsx

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { api } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ==========================================
  // Helpers
  // ==========================================

  const saveToken = (token) => {
    localStorage.setItem("greenmind_token", token);
  };

  const removeToken = () => {
    localStorage.removeItem("greenmind_token");
  };

  const getToken = () => {
    return localStorage.getItem("greenmind_token");
  };

  // ==========================================
  // Check Authentication on App Start
  // ==========================================

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getToken();

        if (!token) {
          setUser(null);
          return;
        }

        const userData = await api.get("/api/auth/me");

        setUser(userData);
      } catch (error) {
        console.error("Authentication check failed:", error);

        removeToken();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // ==========================================
  // Login
  // ==========================================

  const login = async (email, password) => {
    setLoading(true);

    try {
      const data = await api.post("/api/auth/login", {
        email,
        password,
      });

      saveToken(data.access_token);

      setUser(data.user);

      return data.user;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Register
  // ==========================================

  const register = async (
    username,
    email,
    password
  ) => {
    setLoading(true);

    try {
      const data = await api.post(
        "/api/auth/register",
        {
          username,
          email,
          password,
        }
      );

      saveToken(data.access_token);

      setUser(data.user);

      return data.user;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Logout
  // ==========================================

  const logout = async () => {
    try {
      await api.post("/api/auth/logout", {});
    } catch (error) {
      console.warn(
        "Logout API unavailable. Clearing local session.",
        error
      );
    } finally {
      removeToken();
      setUser(null);
    }
  };

  // ==========================================
  // Refresh User Profile
  // ==========================================

  const refreshUser = async () => {
    try {
      const userData = await api.get(
        "/api/auth/me"
      );

      setUser(userData);

      return userData;
    } catch (error) {
      console.error(
        "Failed to refresh user profile:",
        error
      );

      if (error.status === 401) {
        removeToken();
        setUser(null);
      }

      return null;
    }
  };

  // ==========================================
  // Refresh Access Token
  // ==========================================

  const refreshAccessToken = async () => {
    try {
      const response = await api.post(
        "/api/auth/token/refresh",
        {}
      );

      if (response?.access_token) {
        saveToken(response.access_token);
        return response.access_token;
      }

      return null;
    } catch (error) {
      console.error(
        "Token refresh failed:",
        error
      );

      removeToken();
      setUser(null);

      return null;
    }
  };

  // ==========================================
  // Context Value
  // ==========================================

  const value = useMemo(
    () => ({
      user,
      loading,

      login,
      register,
      logout,

      refreshUser,
      refreshAccessToken,

      setUser,
    }),
    [user, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// ==========================================
// Custom Hook
// ==========================================

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used within an AuthProvider"
    );
  }

  return context;
};

export default AuthContext;
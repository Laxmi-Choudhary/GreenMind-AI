import React, { createContext, useState, useEffect, useContext } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('greenmind_token');
      if (token) {
        try {
          const userData = await api.get('/api/auth/me');
          setUser(userData);
        } catch (err) {
          console.error("Token validation failed, logging out...", err);
          localStorage.removeItem('greenmind_token');
          setUser(null);
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await api.post('/api/auth/login', { email, password });
      localStorage.setItem('greenmind_token', data.access_token);
      setUser(data.user);
      return data.user;
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    setLoading(true);
    try {
      const data = await api.post('/api/auth/register', { username, email, password });
      localStorage.setItem('greenmind_token', data.access_token);
      setUser(data.user);
      return data.user;
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/auth/logout', {});
    } catch (err) {
      console.warn("Logout endpoint returned error or unavailable, clearing local storage anyway...", err);
    }
    localStorage.removeItem('greenmind_token');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await api.get('/api/auth/me');
      setUser(userData);
      return userData;
    } catch (err) {
      console.error("Failed to refresh user profile data", err);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

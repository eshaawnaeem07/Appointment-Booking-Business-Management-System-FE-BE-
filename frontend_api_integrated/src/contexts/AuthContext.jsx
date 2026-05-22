import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app load, try to restore session from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Decode the JWT to get user info (role, email, id)
      const payload = JSON.parse(atob(access_token.split('.')[1]));
      const userData = {
        id: payload.sub,        // or payload.user_id depending on your token
        email: payload.email || email,
        role: payload.role,
        name: payload.name || email.split('@')[0],
      };
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    } catch (error) {
      const detail = error.response?.data?.detail || 'Login failed';
      return { success: false, error: detail };
    }
  };

  const register = async (email, password, role, name) => {
    try {
      await api.post('/auth/register', { email, password, role, name });
      // After successful registration, you can either auto-login or redirect to login
      return { success: true };
    } catch (error) {
      const detail = error.response?.data?.detail || 'Registration failed';
      return { success: false, error: detail };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
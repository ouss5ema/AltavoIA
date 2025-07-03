import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("sessionId") || "");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  }, [token]);

  useEffect(() => {
    if (sessionId) localStorage.setItem("sessionId", sessionId);
    else localStorage.removeItem("sessionId");
  }, [sessionId]);

  const login = (user, token, sessionId) => {
    setUser(user);
    setToken(token);
    setSessionId(sessionId);
  };

  const logout = () => {
    setUser(null);
    setToken("");
    setSessionId("");
    localStorage.clear();
  };

  return (
    <AuthContext.Provider value={{ user, token, sessionId, login, logout, loading, setLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
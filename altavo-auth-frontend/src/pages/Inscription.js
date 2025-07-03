import React, { useState, useContext } from "react";
import api from "../api/axios";
import Notification from "../components/Notification";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "../App.css";

export default function Inscription() {
  const [form, setForm] = useState({ email: "", username: "", password: "", confirmPassword: "" });
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/auth/register", form);
      setNotif({ open: true, message: "Inscription réussie ! Connectez-vous.", severity: "success" });
      setTimeout(() => navigate("/connexion"), 1500);
    } catch (err) {
      setNotif({ open: true, message: err.response?.data?.message || "Erreur lors de l'inscription", severity: "error" });
    }
    setLoading(false);
  };

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <img src="/logo-altavo.png" alt="Altavo Logo" className="auth-logo" />
        <h2 className="auth-title">Inscription</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <input
            className="auth-input"
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
            autoFocus
          />
          <input
            className="auth-input"
            type="text"
            name="username"
            placeholder="Nom d'utilisateur"
            value={form.username}
            onChange={handleChange}
            required
          />
          <div className="auth-password-wrapper">
            <input
              className="auth-input"
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Mot de passe"
              value={form.password}
              onChange={handleChange}
              required
            />
            <span
              className="auth-eye"
              onClick={() => setShowPassword((v) => !v)}
              tabIndex={0}
              role="button"
              aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            >
              {showPassword ? (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#23589C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 1l22 22"/><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19C7 19 2.73 15.11 1 12c.74-1.32 2.1-3.29 4.06-5.06M9.5 9.5a3 3 0 0 1 4.5 4.5"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/><path d="M9.88 9.88L4.06 4.06"/><path d="M14.12 14.12l5.82 5.82"/></svg>
              ) : (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#23589C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12C2.73 15.11 7 19 12 19s9.27-3.89 11-7c-1.73-3.11-6-7-11-7S2.73 8.89 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
              )}
            </span>
          </div>
          <div className="auth-password-wrapper">
            <input
              className="auth-input"
              type={showConfirm ? "text" : "password"}
              name="confirmPassword"
              placeholder="Confirmer le mot de passe"
              value={form.confirmPassword}
              onChange={handleChange}
              required
            />
            <span
              className="auth-eye"
              onClick={() => setShowConfirm((v) => !v)}
              tabIndex={0}
              role="button"
              aria-label={showConfirm ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            >
              {showConfirm ? (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#23589C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 1l22 22"/><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19C7 19 2.73 15.11 1 12c.74-1.32 2.1-3.29 4.06-5.06M9.5 9.5a3 3 0 0 1 4.5 4.5"/><path d="M14.12 14.12A3 3 0 0 1 9.88 9.88"/><path d="M9.88 9.88L4.06 4.06"/><path d="M14.12 14.12l5.82 5.82"/></svg>
              ) : (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#23589C" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12C2.73 15.11 7 19 12 19s9.27-3.89 11-7c-1.73-3.11-6-7-11-7S2.73 8.89 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
              )}
            </span>
          </div>
          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? "Inscription..." : "S'inscrire"}
          </button>
        </form>
        <a className="auth-link" href="/connexion">Déjà un compte ? Se connecter</a>
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
import React, { useState } from "react";
import api from "../api/axios";
import Notification from "../components/Notification";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function ResetPassword() {
  const [form, setForm] = useState({
    token: localStorage.getItem("resetToken") || "",
    newPassword: "",
    confirmPassword: "",
  });
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });
  const [loading, setLoading] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/auth/reset-password", form);
      setNotif({ open: true, message: "Mot de passe réinitialisé !", severity: "success" });
      setTimeout(() => {
        localStorage.removeItem("resetToken");
        navigate("/connexion");
      }, 1200);
    } catch (err) {
      setNotif({ open: true, message: err.response?.data?.message || "Erreur lors de la réinitialisation", severity: "error" });
    }
    setLoading(false);
  };

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <img src="/logo-altavo.png" alt="Altavo Logo" className="auth-logo" />
        <h2 className="auth-title">Nouveau mot de passe</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <input
            className="auth-input"
            type="text"
            name="token"
            placeholder="Token de réinitialisation"
            value={form.token}
            onChange={handleChange}
            required
          />
          <div className="auth-password-wrapper">
            <input
              className="auth-input"
              type={showNew ? "text" : "password"}
              name="newPassword"
              placeholder="Nouveau mot de passe"
              value={form.newPassword}
              onChange={handleChange}
              required
            />
            <span
              className="auth-eye"
              onClick={() => setShowNew((v) => !v)}
              tabIndex={0}
              role="button"
              aria-label={showNew ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            >
              {showNew ? (
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
            {loading ? "Réinitialisation..." : "Réinitialiser"}
          </button>
        </form>
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
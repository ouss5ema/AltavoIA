import React, { useState } from "react";
import api from "../api/axios";
import Notification from "../components/Notification";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function ResetPasswordInit() {
  const [email, setEmail] = useState("");
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/auth/reset-password/initiate", { email });
      setNotif({ open: true, message: "Si l'email existe, un lien/code a été envoyé.", severity: "success" });
      if (res.data.token) {
        localStorage.setItem("resetToken", res.data.token);
        setTimeout(() => navigate("/reset-password"), 1200);
      }
    } catch (err) {
      setNotif({ open: true, message: "Erreur lors de la demande", severity: "error" });
    }
    setLoading(false);
  };

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <img src="/logo-altavo.png" alt="Altavo Logo" className="auth-logo" />
        <h2 className="auth-title">Réinitialiser le mot de passe</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <input
            className="auth-input"
            type="email"
            name="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? "Envoi..." : "Envoyer le lien/code"}
          </button>
        </form>
        <a className="auth-link" href="/connexion">Retour à la connexion</a>
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
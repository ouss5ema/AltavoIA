import React, { useState, useContext } from "react";
import api from "../api/axios";
import Notification from "../components/Notification";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "../App.css";

export default function VerificationAppareil() {
  const [code, setCode] = useState("");
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const userId = localStorage.getItem("pendingUserId");
  const fingerprint = localStorage.getItem("pendingFingerprint");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/verification/verify-device", {
        userId,
        fingerprint,
        code,
      });
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      localStorage.setItem("sessionId", res.data.sessionId);
      login(res.data.user, res.data.token, res.data.sessionId);
      setNotif({ open: true, message: "Appareil vérifié, connexion réussie !", severity: "success" });
      setTimeout(() => {
        localStorage.removeItem("pendingUserId");
        localStorage.removeItem("pendingFingerprint");
        navigate("/iaassistant");
      }, 1200);
    } catch (err) {
      setNotif({ open: true, message: err.response?.data?.message || "Erreur de vérification", severity: "error" });
    }
    setLoading(false);
  };

  const handleResend = async () => {
    try {
      await api.post("/verification/resend-code", { userId, fingerprint });
      setNotif({ open: true, message: "Code renvoyé ! Vérifiez votre email ou la console.", severity: "info" });
    } catch (err) {
      setNotif({ open: true, message: "Erreur lors de l'envoi du code", severity: "error" });
    }
  };

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <img src="/logo-altavo.png" alt="Altavo Logo" className="auth-logo" />
        <h2 className="auth-title">Vérification d'appareil</h2>
        <p className="auth-desc">Saisissez le code reçu par email pour activer votre session.</p>
        <form onSubmit={handleSubmit} className="auth-form">
          <input
            className="auth-input"
            type="text"
            name="code"
            placeholder="Code de vérification"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            autoFocus
          />
          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? "Vérification..." : "Vérifier"}
          </button>
        </form>
        <button className="auth-link" style={{marginTop:8}} onClick={handleResend} type="button">Renvoyer le code</button>
        <a className="auth-link" href="/connexion">Retour à la connexion</a>
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
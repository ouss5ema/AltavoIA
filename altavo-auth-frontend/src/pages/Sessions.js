import React, { useEffect, useState } from "react";
import api from "../api/axios";
import Notification from "../components/Notification";
import "../App.css";

export default function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await api.get("/auth/sessions");
        setSessions(res.data.sessions);
      } catch (err) {
        setNotif({ open: true, message: "Erreur lors du chargement des sessions", severity: "error" });
      }
    };
    fetchSessions();
  }, []);

  return (
    <div className="profile-bg">
      <div className="profile-card">
        <h2 className="profile-title">Mes sessions actives</h2>
        <div className="sessions-list">
          {sessions.length === 0 && (
            <div className="session-item">Aucune session active.</div>
          )}
          {sessions.map((session) => (
            <div className="session-item" key={session.id}>
              <div><span className="profile-label">Session ID :</span> {session.id}</div>
              <div><span className="profile-label">Appareil :</span> {session.device_fingerprint}</div>
              <div><span className="profile-label">IP :</span> {session.ip_address}</div>
              <div><span className="profile-label">Dernier accès :</span> {session.last_accessed_at}</div>
              <div><span className="profile-label">Statut :</span> {session.status === "active" ? "Active" : session.status}</div>
            </div>
          ))}
        </div>
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
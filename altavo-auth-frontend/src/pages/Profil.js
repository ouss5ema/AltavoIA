import React, { useContext, useEffect, useState } from "react";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import Notification from "../components/Notification";
import "../App.css";

export default function Profil() {
  const { user } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const [notif, setNotif] = useState({ open: false, message: "", severity: "info" });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get("/auth/profile");
        setProfile(res.data.user);
      } catch (err) {
        setNotif({ open: true, message: "Erreur lors du chargement du profil", severity: "error" });
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="profile-bg">
      <div className="profile-card">
        <h2 className="profile-title">Mon profil</h2>
        {profile && (
          <div className="profile-info">
            <div><span className="profile-label">Nom d'utilisateur :</span> {profile.username}</div>
            <div><span className="profile-label">Email :</span> {profile.email}</div>
            <div><span className="profile-label">Rôle :</span> {profile.role === 1 ? "Utilisateur" : "Admin"}</div>
            <div><span className="profile-label">Status :</span> {profile.status === 1 ? "Actif" : "Inactif"}</div>
          </div>
        )}
      </div>
      <Notification open={notif.open} onClose={() => setNotif({ ...notif, open: false })} severity={notif.severity} message={notif.message} />
    </div>
  );
}
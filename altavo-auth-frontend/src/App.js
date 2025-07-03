import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
// import Navbar from "./components/Navbar";
import Accueil from "./pages/Accueil";
import Connexion from "./pages/Connexion";
import Inscription from "./pages/Inscription";
import VerificationAppareil from "./pages/VerificationAppareil";
import ResetPasswordInit from "./pages/ResetPasswordInit";
import ResetPassword from "./pages/ResetPassword";
import LandingPage from "./pages/LandingPage";
import AIAssistant from "./pages/AIAssistant";
import { useContext } from "react";
import { AuthContext } from "./context/AuthContext";

function App() {
  const { user } = useContext(AuthContext);
  // const location = useLocation();

  return (
    <>
      {/* Navbar supprimé partout */}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/connexion" element={!user ? <Connexion /> : <Navigate to="/iaassistant" />} />
        <Route path="/inscription" element={!user ? <Inscription /> : <Navigate to="/iaassistant" />} />
        <Route path="/verification-appareil" element={<VerificationAppareil />} />
        <Route path="/reset-password-init" element={<ResetPasswordInit />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/iaassistant" element={user ? <AIAssistant /> : <Navigate to="/connexion" />} />
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </>
  );
}

export default function AppWithRouter() {
  return (
    <Router>
      <App />
    </Router>
  );
}
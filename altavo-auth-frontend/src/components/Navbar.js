import React, { useContext } from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/connexion");
  };

  return (
    <AppBar position="static" color="primary" elevation={2}>
      <Toolbar>
        <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, color: "#fff", textDecoration: "none" }}>
          Altavo Partners
        </Typography>
        {user ? (
          <Box>
            <Button color="inherit" component={Link} to="/profil">
              Profil
            </Button>
            <Button color="inherit" component={Link} to="/sessions">
              Sessions
            </Button>
            <Button color="inherit" onClick={handleLogout}>
              Déconnexion
            </Button>
          </Box>
        ) : (
          <Box>
            <Button color="inherit" component={Link} to="/connexion">
              Connexion
            </Button>
            <Button color="inherit" component={Link} to="/inscription">
              Inscription
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
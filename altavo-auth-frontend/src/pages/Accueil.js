import React from "react";
import { Container, Typography, Box, Button } from "@mui/material";
import { Link } from "react-router-dom";

export default function Accueil() {
  return (
    <Container maxWidth="sm" sx={{ mt: 8, textAlign: "center" }}>
      <Typography variant="h3" gutterBottom>
        Bienvenue sur Altavo Partners
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Plateforme d’authentification moderne et sécurisée.
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button variant="contained" color="primary" size="large" component={Link} to="/connexion" sx={{ mr: 2 }}>
          Connexion
        </Button>
        <Button variant="outlined" color="secondary" size="large" component={Link} to="/inscription">
          Inscription
        </Button>
      </Box>
    </Container>
  );
}
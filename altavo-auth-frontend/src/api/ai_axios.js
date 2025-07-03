import axios from "axios";

const ai_api = axios.create({
  baseURL: "http://localhost:8000", // L'URL du backend FastAPI
  headers: {
    // Note: Content-Type est souvent défini par le navigateur pour les uploads de fichiers (multipart/form-data)
    // Il est donc préférable de ne pas le forcer en 'application/json' ici.
  },
});

// Intercepteur pour ajouter le token JWT à chaque requête vers le backend AI
ai_api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default ai_api; 
// API Configuration
// Set VITE_API_URL in a .env file to point the frontend at a different backend.
const API_BASE_URL =
  (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export default API_BASE_URL;

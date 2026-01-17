// API Configuration
// Set VITE_API_URL environment variable for production, defaults to localhost for development
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "https://carbondrop.onrender.com";

export default API_BASE_URL;

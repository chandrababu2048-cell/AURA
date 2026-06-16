// src/services/api.js
// ------------------------------------------------------------
// Central axios instance. All API calls go through here.
// Base URL comes from VITE_API_BASE_URL (see .env.example).
// ------------------------------------------------------------

import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Normalize errors so callers get a plain Error with a useful message.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.message ||
      "Unknown error";
    return Promise.reject(new Error(message));
  },
);

export default api;

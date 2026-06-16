// src/services/authService.js
// ------------------------------------------------------------
// Auth endpoints. Matches api/main.py:
//
//   POST /auth/login    body { email, password }            -> AuthResponse
//   POST /auth/register body { name, email, password, ... } -> AuthResponse
//
// AuthResponse: { success, message?, user? }
// ------------------------------------------------------------

import api from "./api";

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function register({ name, email, password, ai_name }) {
  const body = { name, email, password };
  if (ai_name) body.ai_name = ai_name;
  const { data } = await api.post("/auth/register", body);
  return data;
}

export async function fetchUser(userId) {
  const { data } = await api.get(`/users/${userId}`);
  return data;
}

export async function updateAiName(userId, ai_name) {
  const { data } = await api.patch(`/users/${userId}/ai-name`, { ai_name });
  return data;
}

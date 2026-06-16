// src/services/chatService.js
// ------------------------------------------------------------
// Chat endpoints. Matches api/main.py exactly:
//
//   POST   /chat/think              body { user_id, message, mode } -> { reply }
//   DELETE /chat/session/{user_id}
//   GET    /conversations?user_id&limit
// ------------------------------------------------------------

import api from "./api";

export async function sendMessage(userId, message, mode = "Personal") {
  const { data } = await api.post("/chat/think", {
    user_id: userId,
    message,
    mode,
  });
  return data?.reply ?? "";
}

export async function clearSession(userId) {
  const { data } = await api.delete(`/chat/session/${userId}`);
  return data;
}

export async function fetchRecentMessages(userId, limit = 20) {
  const { data } = await api.get("/conversations", {
    params: { user_id: userId, limit },
  });
  return data ?? [];
}

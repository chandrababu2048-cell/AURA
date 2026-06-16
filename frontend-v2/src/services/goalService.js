// src/services/goalService.js
// ------------------------------------------------------------
// Goals endpoints. Matches api/main.py:
//
//   GET    /goals?user_id
//   POST   /goals          body { user_id, goal_text, deadline? }
//   PATCH  /goals/{id}/complete body { user_id }
//   DELETE /goals/{id}?user_id
// ------------------------------------------------------------

import api from "./api";

export async function fetchGoals(userId) {
  const { data } = await api.get("/goals", { params: { user_id: userId } });
  return data ?? [];
}

export async function createGoal(userId, goal_text, deadline) {
  const body = { user_id: userId, goal_text };
  if (deadline) body.deadline = deadline;
  const { data } = await api.post("/goals", body);
  return data;
}

export async function completeGoal(userId, goalId) {
  const { data } = await api.patch(`/goals/${goalId}/complete`, {
    user_id: userId,
  });
  return data;
}

export async function removeGoal(userId, goalId) {
  const { data } = await api.delete(`/goals/${goalId}`, {
    params: { user_id: userId },
  });
  return data;
}

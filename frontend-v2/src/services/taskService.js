// src/services/taskService.js
// ------------------------------------------------------------
// Plans (daily tasks) endpoints. Matches api/main.py:
//
//   GET    /plans?user_id&date?
//   POST   /plans                 body { user_id, plan_text, planned_for? }
//   PATCH  /plans/{plan_id}/toggle body { user_id }
//   DELETE /plans/{plan_id}?user_id
// ------------------------------------------------------------

import api from "./api";

export async function fetchPlans(userId, date) {
  const params = { user_id: userId };
  if (date) params.date = date;
  const { data } = await api.get("/plans", { params });
  return data ?? [];
}

export async function createPlan(userId, plan_text, planned_for) {
  const body = { user_id: userId, plan_text };
  if (planned_for) body.planned_for = planned_for;
  const { data } = await api.post("/plans", body);
  return data;
}

export async function togglePlan(userId, planId) {
  const { data } = await api.patch(`/plans/${planId}/toggle`, {
    user_id: userId,
  });
  return data;
}

export async function removePlan(userId, planId) {
  const { data } = await api.delete(`/plans/${planId}`, {
    params: { user_id: userId },
  });
  return data;
}

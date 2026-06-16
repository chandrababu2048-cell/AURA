// src/services/stateService.js
// ------------------------------------------------------------
// Digital Twin snapshot. Matches api/main.py:
//
//   GET /state?user_id -> { stress, mood, energy, focus,
//                           active_goals, overdue_tasks }
// ------------------------------------------------------------

import api from "./api";

export async function fetchBossState(userId) {
  const { data } = await api.get("/state", { params: { user_id: userId } });
  return data;
}

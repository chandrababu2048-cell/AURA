// src/services/memoryService.js
// ------------------------------------------------------------
// Memory + weather endpoints.
//
//   GET /memory/context?user_id -> { context }
//   GET /memory/report?user_id  -> { report }
//   GET /weather?city?          -> WeatherResponse
//   GET /news                   -> NewsResponse
// ------------------------------------------------------------

import api from "./api";

export async function fetchContext(userId) {
  const { data } = await api.get("/memory/context", {
    params: { user_id: userId },
  });
  return data?.context ?? "";
}

export async function fetchWeeklyReport(userId) {
  const { data } = await api.get("/memory/report", {
    params: { user_id: userId },
  });
  return data?.report ?? "";
}

export async function fetchWeather(city) {
  const { data } = await api.get("/weather", {
    params: city ? { city } : {},
  });
  return data;
}

export async function fetchNews() {
  const { data } = await api.get("/news");
  return data;
}

/**
 * api.js — All HTTP calls aligned to the actual backend routes.
 *
 * Backend routes (from server.js):
 *   GET  /api/home           → get_home_data   → returns { kpis, yoy, charts, available_years, submission_status }
 *   GET  /api/records        → get_my_records  → returns { rows, available_years, all_years, verification_status }
 *   GET  /api/analytics      → get_analytics   → returns { years, series: { co2_kpi:[{year,value}], ... } }
 *   GET  /api/benchmarks     → get_benchmarks  → returns { bands, scorecard }
 *   GET  /api/companies      → get_companies   → returns [{id,name,email,role,...}]
 *   POST /api/submissions    → submit_data
 *   POST /api/verification   → verify_submission  (MISSING — fixed separately)
 *   GET  /api/reports        → get_reports     (stub)
 *   GET  /api/admin          → get_admin       (stub)
 */
import axios from "axios";

const http = axios.create({ baseURL: "/api", timeout: 30000 });

// Attach auth headers from localStorage on every request
http.interceptors.request.use((cfg) => {
  try {
    const u = JSON.parse(localStorage.getItem("esg_user") || "null");
    if (u) {
      cfg.headers["X-Company-Id"] = u.id   || "";
      cfg.headers["X-Company"]    = u.name || "";
      cfg.headers["X-Role"]       = u.role || "";
    }
  } catch (_) {}
  return cfg;
});

export const api = {
  // ── Auth ──────────────────────────────────────────────────────────────────
  login: (email, password) =>
    http.post("/auth/login", { email, password }).then(r => r.data),

  // ── Home page data (KPI cards + charts + submission status) ───────────────
  // Returns: { company, year, available_years, kpis, yoy, charts, submission_status }
  getHomeData: (company, year) =>
    http.get("/home", { params: { company, year } }).then(r => r.data),

  // ── My Records (template table all years) ─────────────────────────────────
  // Returns: { rows, available_years, all_years, verification_status }
  getMyRecords: (company, year) =>
    http.get("/records", { params: { company, year } }).then(r => r.data),

  // ── Analytics (sector or company KPI series) ──────────────────────────────
  // Returns: { years, series: { co2_kpi:[{year,value}], ... } }
  getAnalytics: (params) => http.get("/analytics", { params }).then(r => r.data),

  // ── Benchmarks (quartile bands + scorecard) ───────────────────────────────
  // Returns: { bands, scorecard, my_kpis, company_trend }
  getBenchmarks: (year, company) =>
    http.get("/benchmarks", { params: { year, company } }).then(r => r.data),

  // ── Companies list ────────────────────────────────────────────────────────
  // Returns: [{id, name, email, role, ...}]
  getCompanies: (params) =>
    http.get("/companies", { params }).then(r => {
      const d = r.data;
      // Normalize to name strings for selects
      if (Array.isArray(d) && d.length && typeof d[0] === "object")
        return d.map(c => c.name);
      return d;
    }),

  // ── Submit KPI data ────────────────────────────────────────────────────────
  submitData: (payload) => http.post("/submissions", payload).then(r => r.data),

  // ── Verification ──────────────────────────────────────────────────────────
  setVerification: (body) => http.post("/verification", body).then(r => r.data),

  // ── Health ────────────────────────────────────────────────────────────────
  health: () => http.get("/health").then(r => r.data),
};

export default api;
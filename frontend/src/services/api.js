/**
 * api.js — All HTTP calls to the backend.
 * Vite proxies /api → Node.js (port 3001) → Python Functions (port 7071).
 */
import axios from "axios";

const http = axios.create({
  baseURL: "/api",
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// ── Auth interceptor (add token when available) ────────────────────────────
http.interceptors.request.use((config) => {
  const raw = localStorage.getItem("esg_user");
  if (raw) {
    const user = JSON.parse(raw);
    config.headers["X-User-Id"]      = user.company_id || "dss";
    config.headers["X-User-Role"]    = user.role;
  }
  return config;
});

// ── Companies ──────────────────────────────────────────────────────────────
export const getCompanies = (year) =>
  http.get("/companies", { params: { year } }).then((r) => r.data);

// ── Submissions ────────────────────────────────────────────────────────────
export const submitData = (payload) =>
  http.post("/submissions", payload).then((r) => r.data);

export const calculateKPI = (formData) =>
  http.post("/submissions/calculate", formData).then((r) => r.data);

// ── Analytics ──────────────────────────────────────────────────────────────
export const getAnalytics = (params = {}) =>
  http.get("/analytics", { params }).then((r) => r.data);

// ── Benchmarks ─────────────────────────────────────────────────────────────
export const getBenchmarks = (year, companyId = null) =>
  http.get("/benchmarks", { params: { year, company_id: companyId } }).then((r) => r.data);

// ── Health ─────────────────────────────────────────────────────────────────
export const healthCheck = () =>
  http.get("/health").then((r) => r.data);

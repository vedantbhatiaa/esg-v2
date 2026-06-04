/**
 * api.js — All HTTP calls. Vite proxies /api → Node:3001 → Python Functions:7071
 */
import axios from "axios";

const http = axios.create({ baseURL: "/api", timeout: 30000 });

http.interceptors.request.use((cfg) => {
  const raw = localStorage.getItem("esg_user");
  if (raw) {
    try {
      const u = JSON.parse(raw);
      cfg.headers["X-Company"] = u.company || "dss";
      cfg.headers["X-Role"]    = u.is_dss ? "dss" : "client";
    } catch(_) {}
  }
  return cfg;
});

export const api = {
  // Companies — returns array of names or array of objects
  getCompanies: (params) =>
    http.get("/companies", { params }).then(r => {
      const d = r.data;
      // Normalize to plain string array
      if (Array.isArray(d) && d.length && typeof d[0] === "object" && d[0].name)
        return d.map(c => c.name);
      return d;
    }),

  // Analytics — sector + optional company overlay
  getAnalytics: (params) => http.get("/analytics", { params }).then(r => r.data),

  // Benchmarks — year + optional company for company-specific bands
  getBenchmarks: (year, company) =>
    http.get("/benchmarks", { params: { year, company } }).then(r => r.data),

  // Company data — all years summary or single year detail
  getCompanyData: (company, year) =>
    http.get("/company_data", { params: { company, year } }).then(r => r.data),

  // Submit full data — saves to master CSV + parquet version
  submitData: (payload) => http.post("/submissions", payload).then(r => r.data),

  // Live KPI calc (no save)
  calculateKPI: (formData) => http.post("/submissions/calculate", formData).then(r => r.data),

  // Verification status
  setVerification: (body) => http.post("/verification", body).then(r => r.data),

  // Health check
  health: () => http.get("/health").then(r => r.data),
};

export default api;
/**
 * api.js — TIP ESG Platform V2
 * All calls use field names matching Streamlit TemplateInputs.
 */
import axios from "axios";

const http = axios.create({ baseURL: "/api", timeout: 30000 });

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
  // Auth
  login: (email, password) =>
    http.post("/auth/login", { email, password }).then(r => r.data),

  // Home — returns { company, year, available_years, kpi_cards, yoy, yr_kpis, submission_status }
  getHomeData: (company, year) =>
    http.get("/home", { params: { company, year } }).then(r => r.data),

  // My Records — returns { rows, all_years, available_years, verification_status }
  getMyRecords: (company, year) =>
    http.get("/records", { params: { company, year } }).then(r => r.data),

  // Analytics — returns { years, series: { energy_kpi:[{year,value}], ... } }
  getAnalytics: (params) =>
    http.get("/analytics", { params }).then(r => r.data),

  // Benchmarks — returns { year, bands, scorecard, my_kpis, company_trend }
  getBenchmarks: (year, company) =>
    http.get("/benchmarks", { params: { year, company } }).then(r => r.data),

  // Companies list
  getCompanies: (params) =>
    http.get("/companies", { params }).then(r => {
      const d = r.data;
      if (Array.isArray(d) && d.length && typeof d[0] === "object")
        return d.map(c => c.name);
      return d;
    }),

  // Submit — data uses Streamlit field names (production, nat_gas, etc)
  submitData: (payload) =>
    http.post("/submissions", payload).then(r => r.data),

  // Verification
  setVerification: (body) =>
    http.post("/verification", body).then(r => r.data),

  health: () => http.get("/health").then(r => r.data),
};

export default api;
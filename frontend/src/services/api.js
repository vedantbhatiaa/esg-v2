/**
 * api.js — TIP ESG Platform V2
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
  login: (email, password) =>
    http.post("/auth/login", { email, password }).then(r => r.data),

  // Home page data — {kpi_cards, yoy, yr_kpis, available_years, submission_status}
  getHomeData: (company, year) =>
    http.get("/home", { params: { company, year } }).then(r => r.data),

  // My Records — {rows, all_years, available_years, verification_status}
  getMyRecords: (company, year) =>
    http.get("/records", { params: { company, year } }).then(r => r.data),

  // Company raw data — WITHOUT year: {years, summary:[{year,raw,kpis}]}
  //                  — WITH year:    {year, raw, kpis, available_years}
  getCompanyData: (company, year) =>
    http.get("/company-data", { params: { company, year } }).then(r => r.data),

  // Analytics — {years, series:{co2_kpi:[{year,value}], ...}}
  getAnalytics: (params) =>
    http.get("/analytics", { params }).then(r => r.data),

  // Benchmarks — {year, bands, scorecard, my_kpis, company_trend}
  getBenchmarks: (year, company) =>
    http.get("/benchmarks", { params: { year, company } }).then(r => r.data),

  // Companies list — normalised to name strings
  getCompanies: (params) =>
    http.get("/companies", { params }).then(r => {
      const d = r.data;
      if (Array.isArray(d) && d.length && typeof d[0] === "object")
        return d.map(c => c.name);
      return d;
    }),

  submitData: (payload) =>
    http.post("/submissions", payload).then(r => r.data),

  setVerification: (body) =>
    http.post("/verification", body).then(r => r.data),

  health: () => http.get("/health").then(r => r.data),
};

export default api;
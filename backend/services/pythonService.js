/**
 * pythonService.js
 * Single place that calls the Python Azure Functions.
 * All routes call this — swap the base URL here when deploying.
 */
const axios = require("axios");

const BASE = process.env.PYTHON_SERVICE_URL || "http://localhost:7071/api";

const python = axios.create({
  baseURL: BASE,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// Generic error wrapper
async function call(method, path, payload = null, params = null) {
  try {
    const res = await python({ method, url: path, data: payload, params });
    return { data: res.data, error: null };
  } catch (err) {
    const msg = err.response?.data?.error || err.message;
    console.error(`[pythonService] ${method.toUpperCase()} ${path} — ${msg}`);
    return { data: null, error: msg };
  }
}

module.exports = {
  getCompanies:  (params)         => call("get",  "/get_companies", null, params),
  getAnalytics:  (params)         => call("get",  "/get_analytics", null, params),
  getBenchmarks: (params)         => call("get",  "/get_benchmarks", null, params),
  submitData:    (body)           => call("post", "/submit_data", body),
  calculateKPI:  (body)           => call("post", "/calculate_kpi", body),
};

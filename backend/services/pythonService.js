/**
 * pythonService.js
 * Single gateway for all Python Azure Function calls.
 * Swap BASE URL here when deploying to Azure.
 */
const axios = require("axios");

const BASE = process.env.PYTHON_SERVICE_URL || "http://localhost:7071/api";

const python = axios.create({
  baseURL: BASE,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

async function call(method, path, payload = null, params = null) {
  try {
    const res = await python({ method, url: path, data: payload, params });
    return { data: res.data, error: null };
  } catch (err) {
    const msg = err.response?.data?.error || err.message;
    console.error(`[python] ${method.toUpperCase()} ${path} — ${msg}`);
    return { data: null, error: msg };
  }
}

module.exports = {
  call,
  authenticate:         (body)   => call("post", "/authenticate",            body),
  getCompanies:         (params) => call("get",  "/get_companies",            null, params),
  getHomeData:          (params) => call("get",  "/get_home_data",            null, params),
  getAnalytics:         (params) => call("get",  "/get_analytics",            null, params),
  getBenchmarks:        (params) => call("get",  "/get_benchmarks",           null, params),
  getMyRecords:         (params) => call("get",  "/get_my_records",           null, params),
  getReports:           (params) => call("get",  "/get_reports",              null, params),
  submitData:           (body)   => call("post", "/submit_data",              body),
  calculateKPI:         (body)   => call("post", "/calculate_kpi",            body),
  getVerificationQueue: (params) => call("get",  "/get_verification_queue",   null, params),
  verifySubmission:     (body)   => call("post", "/verify_submission",        body),
};

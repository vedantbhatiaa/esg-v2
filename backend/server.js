require("dotenv").config();
const express = require("express");
const cors    = require("cors");
const morgan  = require("morgan");

const app  = express();
const PORT = process.env.PORT || 3001;

app.use(cors({ origin: process.env.CORS_ORIGIN || "http://localhost:5173" }));
app.use(express.json({ limit: "2mb" }));
app.use(morgan("dev"));

// ── Route modules ──────────────────────────────────────────────────────────────
app.use("/api/auth",         require("./routes/auth"));
app.use("/api/companies",    require("./routes/companies"));
app.use("/api/home",         require("./routes/home"));
app.use("/api/analytics",    require("./routes/analytics"));
app.use("/api/benchmarks",   require("./routes/benchmarks"));
app.use("/api/submissions",  require("./routes/submissions"));
app.use("/api/records",      require("./routes/records"));
app.use("/api/reports",      require("./routes/reports"));
app.use("/api/verification", require("./routes/verification"));
app.use("/api/company-data", require("./routes/company_data"));   // ← NEW
app.use("/api/admin",        require("./routes/admin"));

app.get("/api/health", (_, res) => res.json({ status: "ok", service: "esg-backend-v2" }));

app.use((err, req, res, next) => {
  console.error("[ESG API Error]", err.message);
  res.status(500).json({ error: err.message || "Internal server error" });
});

app.listen(PORT, () => {
  console.log(`\n  ESG Backend running at http://localhost:${PORT}`);
  console.log(`  Python Functions at ${process.env.PYTHON_SERVICE_URL || "http://localhost:7071/api"}\n`);
});
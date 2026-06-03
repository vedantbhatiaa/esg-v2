require("dotenv").config();
const express = require("express");
const cors    = require("cors");
const morgan  = require("morgan");

const companiesRouter  = require("./routes/companies");
const analyticsRouter  = require("./routes/analytics");
const benchmarksRouter = require("./routes/benchmarks");
const submissionsRouter = require("./routes/submissions");

const app  = express();
const PORT = process.env.PORT || 3001;

app.use(cors({ origin: "http://localhost:5173" }));   // Vue dev server
app.use(express.json());
app.use(morgan("dev"));

// ── Routes ─────────────────────────────────────────────────────────────────
app.use("/api/companies",   companiesRouter);
app.use("/api/analytics",   analyticsRouter);
app.use("/api/benchmarks",  benchmarksRouter);
app.use("/api/submissions", submissionsRouter);

app.get("/api/health", (req, res) => res.json({ status: "ok", service: "esg-backend" }));

app.listen(PORT, () => {
  console.log(`\n  ESG Backend running at http://localhost:${PORT}`);
  console.log(`  Proxying Python Functions at ${process.env.PYTHON_SERVICE_URL}\n`);
});

const express = require("express");
const router  = express.Router();
const { getBenchmarks } = require("../services/pythonService");

// GET /api/benchmarks?year=2023&company_id=verdatyres
router.get("/", async (req, res) => {
  const { data, error } = await getBenchmarks(req.query);
  if (error) return res.status(500).json({ error });
  res.json(data);
});

module.exports = router;

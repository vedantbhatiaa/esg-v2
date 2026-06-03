const express = require("express");
const router  = express.Router();
const { submitData, calculateKPI } = require("../services/pythonService");

// POST /api/submissions  — save a completed submission
router.post("/", async (req, res) => {
  const { data, error } = await submitData(req.body);
  if (error) return res.status(500).json({ error });
  res.json(data);
});

// POST /api/submissions/calculate  — live KPI calc (no save)
router.post("/calculate", async (req, res) => {
  const { data, error } = await calculateKPI(req.body);
  if (error) return res.status(500).json({ error });
  res.json(data);
});

module.exports = router;

const express = require("express");
const router  = express.Router();
const { getCompanies } = require("../services/pythonService");

// GET /api/companies?year=2023
router.get("/", async (req, res) => {
  const { data, error } = await getCompanies(req.query);
  if (error) return res.status(500).json({ error });
  res.json(data);
});

module.exports = router;

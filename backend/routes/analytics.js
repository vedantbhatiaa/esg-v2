const express = require("express");
const router  = express.Router();
const { getAnalytics } = require("../services/pythonService");

// GET /api/analytics?company_id=verdatyres&year_from=2009&year_to=2023
router.get("/", async (req, res) => {
  const { data, error } = await getAnalytics(req.query);
  if (error) return res.status(500).json({ error });
  res.json(data);
});

module.exports = router;

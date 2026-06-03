const express = require("express");
const router  = express.Router();
const ps      = require("../services/pythonService");
router.get("/companies", async (req, res, next) => {
  const { data, error } = await ps.getCompanies();
  if (error) return res.status(500).json({ error });
  res.json(data);
});
module.exports = router;

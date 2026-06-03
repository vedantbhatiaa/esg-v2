const express = require("express");
const router  = express.Router();
const ps      = require("../services/pythonService");
router.get("/",  async (req, res, next) => {
  const { data, error } = await ps.getVerificationQueue(req.query);
  if (error) return res.status(500).json({ error });
  res.json(data);
});
router.post("/", async (req, res, next) => {
  const { data, error } = await ps.verifySubmission(req.body);
  if (error) return res.status(500).json({ error });
  res.json(data);
});
module.exports = router;

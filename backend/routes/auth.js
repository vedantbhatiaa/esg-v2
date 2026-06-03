const express = require("express");
const router  = express.Router();
const ps      = require("../services/pythonService");
router.post("/login", async (req, res, next) => {
  try {
    const { data, error } = await ps.authenticate(req.body);
    if (error) return res.status(401).json({ error: "Invalid credentials" });
    res.json(data);
  } catch (e) { next(e) }
});
module.exports = router;

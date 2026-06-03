const express = require("express");
const router  = express.Router();
const ps      = require("../services/pythonService");
router.get("/", async (req, res, next) => {
  try {
    const { data, error } = await ps.getMyRecords(req.query);
    if (error) return res.status(500).json({ error });
    res.json(data);
  } catch (e) { next(e) }
});
module.exports = router;

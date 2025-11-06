const express = require('express');
const router = express.Router();
const { searchRecipes } = require('../services/recipeService');

// GET /api/recipes/search?q=chicken
router.get('/search', async (req, res) => {
  const q = req.query.q || req.query.query || '';
  try {
    const results = await searchRecipes(q, 6);
    res.json({ ok: true, results });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: String(err) });
  }
});

module.exports = router;

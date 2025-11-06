const express = require('express');
const router = express.Router();
const db = require('../db');
const { generateResponse } = require('../services/aiService');

// Simple middleware to parse auth token and set req.user if present (non-strict)
const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret';
router.use((req, res, next) => {
  const auth = req.headers.authorization;
  if (auth && auth.startsWith('Bearer ')) {
    try {
      const payload = jwt.verify(auth.slice(7), JWT_SECRET);
      req.user = payload;
    } catch (e) {
      // ignore
    }
  }
  next();
});

// POST /api/chat/query { query: '...' }
router.post('/query', async (req, res) => {
  const { query } = req.body;
  if (!query) return res.status(400).json({ error: 'query required' });

  // load user preferences if user is authenticated
  let prefs = {};
  if (req.user && req.user.id) {
    try {
      const row = await new Promise((resolve, reject) => db.get('SELECT preferences FROM users WHERE id = ?', [req.user.id], (err, r) => err ? reject(err) : resolve(r)));
      prefs = row && row.preferences ? JSON.parse(row.preferences) : {};
    } catch (e) {
      console.warn('failed to load preferences', e);
    }
  }

  try {
    const ai = await generateResponse(query, { preferences: prefs });

    // optionally store message history
    if (req.user && req.user.id) {
      db.run('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)', [req.user.id, 'user', query]);
      db.run('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)', [req.user.id, 'assistant', ai]);
    }

    res.json({ ok: true, result: ai });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: String(err) });
  }
});

module.exports = router;
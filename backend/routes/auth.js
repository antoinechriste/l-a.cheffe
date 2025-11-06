const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../db');

const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret';

router.post('/signup', async (req, res) => {
  const { username, password, preferences } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  const hash = await bcrypt.hash(password, 10);
  db.run('INSERT INTO users (username, password_hash, preferences) VALUES (?, ?, ?)', [username, hash, JSON.stringify(preferences||{})], function(err) {
    if (err) return res.status(400).json({ error: String(err) });
    const token = jwt.sign({ id: this.lastID, username }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ ok: true, token });
  });
});

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  db.get('SELECT * FROM users WHERE username = ?', [username], async (err, row) => {
    if (err) return res.status(500).json({ error: String(err) });
    if (!row) return res.status(401).json({ error: 'invalid credentials' });
    const ok = await bcrypt.compare(password, row.password_hash);
    if (!ok) return res.status(401).json({ error: 'invalid credentials' });
    const token = jwt.sign({ id: row.id, username }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ ok: true, token });
  });
});

module.exports = router;

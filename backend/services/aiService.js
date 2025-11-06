// AI service: uses Hugging Face Inference API (recommended free option) if HUGGINGFACEHUB_API_TOKEN is set.
// Fallback: simple template-based response if no token.
const axios = require('axios');

async function generateResponse(query, context = {}) {
  const hfToken = process.env.HUGGINGFACEHUB_API_TOKEN;
  const model = process.env.HF_MODEL || 'mistralai/mistral-small-3-1-24b-instruct-2503';

  // build prompt including context (preferences, recent messages)
  const prompt = `You are a friendly cooking assistant. Use the user's preferences: ${JSON.stringify(context.preferences||{})}.\n\nUser: ${query}\nAssistant:`;

  if (hfToken) {
    const url = `https://api-inference.huggingface.co/models/${model}`;
    const res = await axios.post(url, { inputs: prompt, parameters: { max_new_tokens: 256, temperature: 0.1 } }, {
      headers: { Authorization: `Bearer ${hfToken}` }
    });
    // Response format may vary; try common shapes
    if (res.data && typeof res.data === 'string') return res.data;
    if (res.data && res.data.generated_text) return res.data.generated_text;
    if (Array.isArray(res.data) && res.data[0] && res.data[0].generated_text) return res.data[0].generated_text;
    return JSON.stringify(res.data);
  }

  // Fallback simple reply
  return `I can help with recipes and meal planning. (No HF token configured; set HUGGINGFACEHUB_API_TOKEN to enable full AI responses.)\nYou asked: ${query}`;
}

module.exports = { generateResponse };

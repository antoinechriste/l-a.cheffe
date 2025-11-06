// Service to call free recipe APIs (Spoonacular or Edamam). Use API keys from env.
const axios = require('axios');

async function searchRecipes(query, num = 5) {
  const spoonKey = process.env.SPOONACULAR_API_KEY;
  if (spoonKey) {
    // Spoonacular free tier example
    const url = `https://api.spoonacular.com/recipes/complexSearch?query=${encodeURIComponent(query)}&number=${num}&apiKey=${spoonKey}`;
    const res = await axios.get(url);
    return res.data.results || [];
  }

  // Edamam fallback (requires app_id/app_key)
  const edamId = process.env.EDAMAM_APP_ID;
  const edamKey = process.env.EDAMAM_APP_KEY;
  if (edamId && edamKey) {
    const url = `https://api.edamam.com/search?q=${encodeURIComponent(query)}&app_id=${edamId}&app_key=${edamKey}&to=${num}`;
    const res = await axios.get(url);
    return (res.data.hits || []).map(h => h.recipe);
  }

  // No external API available: return a minimal canned response
  return [{ title: `No recipe API configured`, sourceUrl: '', summary: `Install SPOONACULAR_API_KEY or EDAMAM_APP_ID/KEY in your .env` }];
}

module.exports = { searchRecipes };

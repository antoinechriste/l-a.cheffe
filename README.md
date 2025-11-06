# CookBot (Full-stack demo)

This project is a sample full-stack cookbook assistant using only free tools and frameworks.
It includes:
- Backend: Node.js + Express, SQLite, JWT auth
- Frontend: React (Vite), Context API for state
- Recipe API integration (Spoonacular or Edamam — free tiers available)
- Local embeddings/LLM via Hugging Face Inference (optional — needs HUGGINGFACEHUB_API_TOKEN)
- Storage: SQLite (local file)

Project layout:
```
cookbot/
  backend/
    server.js
    routes/
      auth.js
      chat.js
      recipes.js
    services/
      aiService.js
      recipeService.js
    db.js
    package.json
    .env.example
  frontend/
    package.json
    src/
      App.jsx
      main.jsx
      components/
        Chat.jsx
        Login.jsx
        Signup.jsx
      context/
        AuthContext.jsx
        ChatContext.jsx
      index.css
  README.md
```

Quick start (development)

1. Backend

```powershell
cd cookbot/backend
npm install
# create .env from .env.example and fill values
# e.g. set JWT_SECRET and optional API keys
# On PowerShell (temporary for current session):
$env:JWT_SECRET = "secret123"
$env:HUGGINGFACEHUB_API_TOKEN = "your_token_here"
$env:SPOONACULAR_API_KEY = "your_spoonacular_key"

npm run dev
```

2. Frontend (in a new terminal)

```powershell
cd cookbot/frontend
npm install
npm run dev
# open the URL printed by Vite (usually http://localhost:5173)
```

Notes and configuration
- Recipes: configure `SPOONACULAR_API_KEY` or Edamam keys in backend `.env` to use real recipe search.
- LLM: configure `HUGGINGFACEHUB_API_TOKEN` to enable the Hugging Face Inference API for high-quality responses. If not set the backend returns a safe fallback message.
- Authentication: JWT tokens are returned on signup/login and stored in frontend localStorage. Protect your JWT secret.
- Database: `backend/data/db.sqlite` created automatically.

How the QA/chat works
- Frontend sends `POST /api/chat/query` with { query }. Backend loads user preferences (if authenticated) and calls `aiService.generateResponse(query, { preferences })`.
- `aiService` will call Hugging Face Inference API if token is set. Otherwise it uses a template fallback.

Deployment hints
- This scaffold is intended for local dev. For deployment, consider:
  - Using a managed DB (MongoDB Atlas or hosted PostgreSQL) instead of SQLite in production
  - Using a proper hosting service for the frontend (Vercel, Netlify) and backend (Render, Fly, etc.)

Git

```bash
cd cookbot
git init
git add .
git commit -m "Initial CookBot scaffold"
# push:
# create a GitHub repo and then:
git remote add origin git@github.com:yourusername/your-repo.git
git push -u origin main
```

If you want, I can:
- Run the backend and frontend here to validate the flow
- Add unit tests and example integration tests
- Implement more robust message storage and user preferences UI

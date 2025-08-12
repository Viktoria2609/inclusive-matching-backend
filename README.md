# KIDNECT — Backend (FastAPI)

Lightweight FastAPI service for profile management and AI-assisted matching.
Provides REST endpoints consumed by the React frontend and OpenAPI docs.

![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![Deploy](https://img.shields.io/badge/Render-live-success)

---

## Live / Docs / Frontend

- **Base URL:** https://inclusive-matching-backend.onrender.com
- **Docs (Swagger):** https://inclusive-matching-backend.onrender.com/docs
- **Frontend Live:** https://inclusive-matching-frontend2.vercel.app
- **Frontend repo:** https://github.com/Viktoria2609/inclusive-matching-frontend2

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment](#environment)
- [Database & Migrations](#database--migrations)
- [Available Commands](#available-commands)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [CORS](#cors)
- [Deployment (Render)](#deployment-render)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This service exposes profile CRUD and **AI matching** endpoints. Data is stored in PostgreSQL
(using SQLAlchemy + Alembic). A small service layer builds prompts and calls an LLM client.
According to `main.py`, **there is no global `/api` prefix** — endpoints are mounted at
`/profiles/*` and `/ai/match`.

---

## Features

- FastAPI with automatic OpenAPI/Swagger docs (`/docs`)
- PostgreSQL via SQLAlchemy ORM and Alembic migrations
- Modular routers: `profiles` mounted at `/profiles`, `ai_match` mounted at `/ai/match`
- Service layer in `app/services/*` (LLM client + prompt builder)
- Pytest test suite for profiles
- CORS configured for localhost, your Vercel app, and any extra origins via env

---

## Tech Stack

FastAPI • Uvicorn • SQLAlchemy ORM • Alembic • Pydantic • Pytest

---

## Project Structure

```text
inclusive-matching-backend
├── alembic/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ai_match.py
│   │   └── profiles.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── matching_prompt.py
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   └── test_profiles.py
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- **Python:** 3.11+
- **PostgreSQL:** 14+ (or managed instance, e.g., Render PostgreSQL)

### Setup

```bash
# 1) Create and activate venv
python -m venv .venv
source ./.venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Create .env from example and fill values
cp .env.example .env

# 4) Apply migrations (first time)
alembic upgrade head

# 5) Run dev server
uvicorn app.main:app --reload
# http://127.0.0.1:8000  (docs at /docs)
```

> In `main.py` have `Base.metadata.create_all(bind=engine)`. For real prodaction **Alembic**; `create_all` полезен только для локального старта/PoC.

---

## Environment

Create a `.env` in the repo root (see `.env.example`). Typical variables:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db_name>

# CORS
# Extra origins to allow (comma-separated). Defaults already include:
# http://localhost:5173, http://127.0.0.1:5173, https://inclusive-matching-frontend2.vercel.app
ALLOWED_ORIGINS=https://your-preview.vercel.app,https://another.app

# (Optional) LLM provider key if AI-matching uses external API
OPENAI_API_KEY=<your-key>

# App
APP_ENV=dev
```

> For Render PostgreSQL, copy the **Internal Database URL** into `DATABASE_URL`
> and make sure the URI includes a driver, e.g., `postgresql+psycopg2://...`.

---

## Database & Migrations

- Initialize DB schema:
  ```bash
  alembic upgrade head
  ```
- Create a new migration after changing models:
  ```bash
  alembic revision --autogenerate -m "add <something>"
  alembic upgrade head
  ```

---

## Available Commands

```bash
# Run local dev
uvicorn app.main:app --reload

# Lint (optional if configured)
python -m ruff check .
python -m black .            # or: black .

# Run tests
pytest -q
```

---

## API Endpoints

### Health
- **GET** `/` → `{"message": "Inclusive Matching API is running!"}`
- **GET** `/healthz` → `{"status": "ok"}`

### Profiles  (mounted at `/profiles`)
| Purpose            | Method | Path                |
|--------------------|--------|---------------------|
| List profiles      | GET    | `/profiles`         |
| Create profile     | POST   | `/profiles`         |
| Get profile by id  | GET    | `/profiles/{id}`    |
| Update profile     | PUT    | `/profiles/{id}`    |
| Delete profile     | DELETE | `/profiles/{id}`    |

### AI Matching  (router prefix `/ai`, endpoint `/match` → `/ai/match`)
**POST** `/ai/match`

**Query params:**
- `target_id` (int, required) — ID of the profile to match from  
- `mode` (`similarity` | `complementarity` | `goal_alignment`, default `complementarity`)  
- `top_k` (int, 1–20, default 5) — number of results to return  
- `same_city` (bool, default `true`) — restrict candidates to the target's city  
- `max_candidates` (int, 1–200, default 50) — DB candidates passed to LLM  
- `language` (string, default `en`) — output language (`en`, `ru`, …)

**200 Response (minimal):**
```json
{
  "target_id": 123,
  "mode": "complementarity",
  "results": [
    { "id": 45, "rationale": "..." },
    { "id": 52, "rationale": "..." }
  ]
}
```

**Errors:**
- `404` — Target profile not found  
- `502` — LLM call failed / invalid JSON / invalid structure

### Examples

**cURL:**
```bash
curl -X POST   "https://inclusive-matching-backend.onrender.com/ai/match?target_id=123&mode=complementarity&top_k=5&same_city=true&max_candidates=50&language=en"
```

**Axios (frontend):**
```js
// baseURL = import.meta.env.VITE_API_URL
await api.post("/ai/match", null, {
  params: {
    target_id: profileId,
    mode: "complementarity",
    top_k: 5,
    same_city: true,
    max_candidates: 50,
    language: "en",
  },
});
```

> Explore and try endpoints in the interactive docs at `/docs`.

---

## Testing

Run all tests (requires an isolated DB or test schema):

```bash
pytest -q
```

Tip: Use a separate `TEST_DATABASE_URL` and configure your tests/fixtures to avoid touching prod data.

---

## CORS

Configured in `main.py`:

- **allow_origins**: default `["http://localhost:5173", "http://127.0.0.1:5173", "https://inclusive-matching-frontend2.vercel.app"]`
- **allow_origin_regex**: `https://.*\.vercel\.app$` (включает любые Vercel preview)
- **ALLOWED_ORIGINS** (env): доп. домены через запятую

Example env:
```bash
ALLOWED_ORIGINS=https://kidnect-preview.vercel.app,https://staging.myapp.com
```

---

## Deployment (Render)

**Quick steps:**
1. Create a **Render PostgreSQL** instance → copy the *Internal Database URL*.
2. Create a **Web Service** from this repo.
3. **Environment:** Python 3.11+.
4. **Build Command:** `pip install -r requirements.txt`  
   **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Add env vars: `DATABASE_URL`, `ALLOWED_ORIGINS`, `APP_ENV`, and `OPENAI_API_KEY` (optional).
6. First deploy may fail if DB is empty; run migrations: `alembic upgrade head`.
7. Verify `/docs` is reachable.

**Optional `render.yaml` (in repo root):**
```yaml
services:
  - type: web
    name: inclusive-matching-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port 10000
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: ALLOWED_ORIGINS
        value: https://inclusive-matching-frontend2.vercel.app,http://localhost:5173
      - key: APP_ENV
        value: prod
      - key: OPENAI_API_KEY
        sync: false
```

---

## Troubleshooting

- **DB connection failed:** ensure `DATABASE_URL` is correct and driver prefix is `postgresql+psycopg2://`.
- **`sslmode` issues on Render:** prefer the *Internal* DB URL (no SSL needed internally). For public URLs add `?sslmode=require`.
- **CORS errors:** confirm your origin is allowed via defaults or `ALLOWED_ORIGINS`.
- **Migrations out of sync:** `alembic history` → `alembic upgrade head`; regenerate if needed.
- **Import errors on start:** Run from repo root; `uvicorn app.main:app`. Ensure `app` is a package.

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/<short-name>`
3. Format & lint; run tests: `pytest -q`
4. Push and open a Pull Request with context


---

## License

MIT 

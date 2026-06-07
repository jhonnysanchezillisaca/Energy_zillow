# Agent Notes

## Repo layout
- `backend/` — FastAPI app. Entrypoint: `backend.main:app`.
- `frontend/` — React + Vite + TypeScript + Tailwind.
- `core/` — Shared domain logic (e.g., LL97 emission factors).
- `etl/` — Data pipeline scripts. **Stale / broken** in current structure (see below).
- `data/` — Pre-generated CSVs required by the backend. App works without running ETL.
- `archive/` — Original refactored scripts. **Reference only.** Do not use for execution.

## Quick start
1. `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. `cp .env.example .env` and add `OPENAI_API_KEY`.
3. Terminal 1 (repo root): `uvicorn backend.main:app --reload --port 8000`
4. Terminal 2: `cd frontend && npm install && npm run dev`

## Build & deploy
- Frontend: `cd frontend && npm run build` (runs `tsc -b && vite build`, outputs to `frontend/dist/`).
- Backend: No build step. CI deploys Python app to Azure Web App (`energyzillowapp`).
- **CORS:** `backend/main.py` hardcodes `allow_origins` to `["http://localhost:5173", "http://localhost:3000"]`. Update before deploying to production.

## Testing
- **No test suite exists.** Do not run `pytest` or `npm test`.

## ETL / Data pipeline
- The ETL scripts in `etl/` are **not fully functional** in the current structure. `etl/transform.py` imports from `archive/Funciones.py`, and `requirements.txt` is missing ETL-only dependencies (`prophet`, `requests`, `matplotlib`).
- The `data/` directory contains committed pre-generated CSVs, so the backend works out of the box without running the pipeline.

## Environment
- Required: `OPENAI_API_KEY` (used by `/api/v1/buildings/{bbl}/recommendations`).
- Optional: `EIA_API_KEY` (only for re-running forecast models), `PORT` (default 8000).
- Backend config and data paths are relative to repo root (`backend/config.py`).

## Frontend quirks
- `vite.config.ts` proxies `/api` to `http://localhost:8000`.
- `tsconfig.json` has `noUnusedLocals` and `noUnusedParameters` enabled. Build fails on unused imports/variables.
- Tailwind and PostCSS are standard setup.

## Gotchas
- Run `uvicorn` from the **repo root** so absolute imports (`backend.*`, `core.*`) resolve correctly.
- `.gitignore` ignores all `*.csv` except `data/*.csv`.

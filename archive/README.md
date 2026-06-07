# Archive

This folder contains the original project files that have been refactored into the new structure.

- `app.py` — Original Streamlit dashboard (moved to `frontend/` as React app)
- `Funciones.py` — Original helper functions (refactored into `backend/services/`)
- `api.py` — Original FastAPI entry point (refactored into `backend/main.py`)
- `Limites.py` — Original emission limits module (moved to `core/emission_limits.py`)
- `startup.sh` — Original deployment startup script (superseded by direct `uvicorn` usage)
- `READ ME.txt` — Original placeholder notes

These files are kept for reference only. The active codebase lives in:
- `backend/` — FastAPI application
- `frontend/` — React + Vite frontend
- `core/` — Shared domain logic (emission factors)
- `etl/` — Data pipeline scripts
- `data/` — CSV datasets

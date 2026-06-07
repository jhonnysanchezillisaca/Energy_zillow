# NYC Building Energy Dashboard

A full-stack demo application that analyzes NYC building energy consumption, calculates LL97 emissions penalties, forecasts future penalties, and generates AI-powered efficiency recommendations.

## What It Does

This dashboard ingests NYC open data (LL84 energy benchmarking + PLUTO property records) to help building owners and consultants understand:

- **Current compliance status** with Local Law 97 emissions limits
- **Projected annual penalties** for 2030, 2035, and 2040
- **Emissions breakdown** by fuel type (electricity, natural gas, fuel oil, others)
- **Future consumption budget expectations** based on projected fuel price fluctuations
- **Personalized efficiency recommendations** generated via OpenAI

## Architecture

```
Energy_zillow/
├── backend/          # FastAPI application
│   ├── main.py       # API routes
│   ├── services/     # Business logic (search, buildings, recommendations)
│   └── models.py     # Pydantic request/response schemas
├── frontend/         # React + Vite + TypeScript + Tailwind + Recharts
│   └── src/
│       ├── pages/    # SearchPage, BuildingPage
│       └── components/ # Charts, tables, recommendations
├── core/             # Shared domain logic
│   └── emission_limits.py  # LL97 factors from 1 RCNY §103-14
├── etl/              # Data pipeline scripts
│   ├── datasets.py
│   ├── transform.py
│   ├── fuels.py
│   ├── predictions.py
│   ├── ranking.py
│   └── forecast_models/  # Prophet-based fuel price forecasting
├── data/             # CSV artifacts (committed for demo purposes)
└── archive/          # Original project files (reference only)
```

## Prerequisites

- Python 3.11+ (3.14 supported)
- Node.js 18+
- OpenAI API key
- (Optional) EIA API key — only needed to re-run fuel price forecast models

## Setup

### 1. Clone & create Python virtual environment

```bash
git clone <repo-url>
cd Energy_zillow
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env and add your keys:
# OPENAI_API_KEY=sk-...
# EIA_API_KEY=...   (optional, for re-running forecast models)
```

### 3. Run the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### 4. Run the frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will open at `http://localhost:5173` and proxy API calls to the backend.

## Data Pipeline

The ETL scripts generate the CSVs in `data/`. For a fresh run:

```bash
# 1. Download raw datasets (requires NYC Open Data URLs)
python etl/datasets.py

# 2. Clean and merge
python etl/transform.py

# 3. Run processing steps
python etl/fuels.py
python etl/information.py
python etl/predictions.py
python etl/ranking.py
python etl/future.py

# 4. (Optional) Re-run fuel price forecasts
export EIA_API_KEY=your_key
python etl/forecast_models/electric.py
python etl/forecast_models/natural_gas.py
python etl/forecast_models/fuel_oil.py
python etl/weight_creator.py
python etl/future.py
```

**Note:** The `data/` folder already contains pre-generated CSVs so the app works out of the box without running the pipeline.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/search?address={addr}` | Fuzzy search building by address |
| GET | `/api/v1/buildings/{bbl}` | Full building detail (info + penalties + fuels + future) |
| GET | `/api/v1/buildings/{bbl}/future` | Future consumption scenarios |
| GET | `/api/v1/buildings/{bbl}/recommendations` | AI-generated efficiency tips |

## Deployment Notes

- **Backend:** Any ASGI host (Render, Railway, Fly.io). Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Frontend:** Static site host (Vercel, Netlify, GitHub Pages). Build command: `npm run build` inside `frontend/`. Output directory: `frontend/dist/`.
- **CORS:** Update `backend/main.py` `allow_origins` to include your production frontend URL.
- **Secrets:** Never commit `.env`. Set environment variables on your hosting platform.

## Tech Stack

- **Backend:** FastAPI, Pydantic, Pandas, RapidFuzz, OpenAI
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, React Router, Axios
- **Data:** Prophet (forecasting), Pandas (ETL)

## License

This is a student/demo project. Data sources: NYC Open Data (LL84, PLUTO), EIA (fuel prices).

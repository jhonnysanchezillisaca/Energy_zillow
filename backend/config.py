import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT_DIR / "data")))

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EIA_API_KEY = os.getenv("EIA_API_KEY", "")
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

# Data files
BASIC_INFO_CSV = DATA_DIR / "basic_information.csv"
FUELS_CSV = DATA_DIR / "fuels.csv"
FUELS_ANALYSIS_CSV = DATA_DIR / "fuels_analisis.csv"
PREDICTIONS_CSV = DATA_DIR / "predictions.csv"
RANKING_CSV = DATA_DIR / "ranking.csv"
FUTURE_CSV = DATA_DIR / "pred_to_display.csv"

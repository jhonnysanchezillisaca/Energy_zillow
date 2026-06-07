from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    BuildingDetail,
    BuildingInfo,
    FuelBreakdown,
    FutureConsumptionScenario,
    PenaltyForecast,
    RecommendationResponse,
    SearchResult,
)
from backend.services.search import search_building
from backend.services.buildings import (
    get_building_info,
    get_fuel_breakdown,
    get_future_consumption,
    get_penalty_forecast,
)
from backend.services.recommendations import generate_recommendations

app = FastAPI(
    title="Energy Dashboard API",
    description="API for building energy search, penalty predictions, and efficiency recommendations.",
    version="1.0.0",
)

# CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Energy Dashboard API is running. Visit /docs to explore endpoints."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/search", response_model=SearchResult)
def search(address: str = Query(..., description="Building address to search for")):
    """Fuzzy-search a building by address and return the best match."""
    result = search_building(address)
    if result is None:
        raise HTTPException(status_code=404, detail="No building found for that address.")
    return result


@app.get("/api/v1/buildings/{bbl}", response_model=BuildingDetail)
def get_building(bbl: int):
    """Return full building details including info, penalties, fuels, and future consumption."""
    info = get_building_info(2024, bbl)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Building with BBL {bbl} not found.")

    penalties = get_penalty_forecast(2024, bbl)
    fuels = get_fuel_breakdown(2024, bbl)
    future = get_future_consumption(bbl)

    return BuildingDetail(
        info=info,
        penalties=penalties,
        fuels=fuels,
        future_consumption=future,
    )


@app.get("/api/v1/buildings/{bbl}/future", response_model=list[FutureConsumptionScenario])
def get_future(bbl: int):
    """Return future consumption scenarios for a building."""
    future = get_future_consumption(bbl)
    if not future:
        raise HTTPException(status_code=404, detail=f"No future consumption data for BBL {bbl}.")
    return future


@app.get("/api/v1/buildings/{bbl}/recommendations", response_model=RecommendationResponse)
def get_recommendations(bbl: int):
    """Generate 5 AI-powered energy efficiency recommendations for a building."""
    try:
        return generate_recommendations(bbl)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

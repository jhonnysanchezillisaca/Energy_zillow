from pydantic import BaseModel
from typing import Optional


class SearchResult(BaseModel):
    bbl: int
    property_name: Optional[str] = None
    address: Optional[str] = None
    match_score: float


class BuildingInfo(BaseModel):
    bbl: int
    calendar_year: int
    property_name: Optional[str] = None
    address: Optional[str] = None
    address_1: Optional[str] = None
    status: bool
    status_text: str
    status_color: str
    ranking: Optional[int] = None
    energy_star_score: Optional[float] = None
    largest_property_use_type_gross_floor_area_ft2: Optional[float] = None
    calculated_emissions: Optional[float] = None
    emissions_limit: Optional[float] = None
    excess_emissions: Optional[float] = None
    difference: Optional[float] = None
    relative_to_limit: Optional[float] = None
    dob_emissions: Optional[float] = None
    penalty: Optional[float] = None


class PenaltyForecast(BaseModel):
    calendar_year: int
    bbl: int
    penalty_2030: Optional[float] = None
    penalty_2035: Optional[float] = None
    penalty_2040: Optional[float] = None


class FuelBreakdown(BaseModel):
    calendar_year: int
    bbl: int
    fuel_oil: Optional[float] = None
    electricity: Optional[float] = None
    natural_gas: Optional[float] = None
    others: Optional[float] = None


class FutureConsumptionScenario(BaseModel):
    year: str
    scenario: str
    value: float


class RecommendationResponse(BaseModel):
    bbl: int
    recommendations: str


class BuildingSnapshot(BaseModel):
    """Aggregate of building data needed for recommendations."""
    info: BuildingInfo
    penalties: Optional[PenaltyForecast] = None
    fuels: Optional[FuelBreakdown] = None


class BuildingDetail(BaseModel):
    info: BuildingInfo
    penalties: Optional[PenaltyForecast] = None
    fuels: Optional[FuelBreakdown] = None
    future_consumption: list[FutureConsumptionScenario] = []

import pandas as pd
import numpy as np
from backend.config import (
    BASIC_INFO_CSV,
    FUELS_CSV,
    FUELS_ANALYSIS_CSV,
    PREDICTIONS_CSV,
    RANKING_CSV,
    FUTURE_CSV,
)
from backend.models import BuildingInfo, PenaltyForecast, FuelBreakdown, FutureConsumptionScenario
from backend.utils.helpers import to_float, status_to_text

# Load all datasets once at import time for fast API responses
_df_basic = pd.read_csv(BASIC_INFO_CSV, low_memory=False)
_df_basic.columns = _df_basic.columns.str.strip()

_df_fuels = pd.read_csv(FUELS_CSV, low_memory=False)
_df_fuels_analysis = pd.read_csv(FUELS_ANALYSIS_CSV, low_memory=False)
_df_predictions = pd.read_csv(PREDICTIONS_CSV, low_memory=False)
_df_ranking = pd.read_csv(RANKING_CSV, low_memory=False)
_df_future = pd.read_csv(FUTURE_CSV, low_memory=False)


def get_building_info(year: int, bbl: int) -> BuildingInfo | None:
    """Return combined building info from ranking, basic info, and fuels datasets."""
    ranking = _df_ranking[(_df_ranking["Calendar Year"] == year) & (_df_ranking["BBL"] == bbl)]
    basic = _df_basic[(_df_basic["Calendar Year"] == year) & (_df_basic["BBL"] == bbl)]
    fuels = _df_fuels[(_df_fuels["Calendar Year"] == year) & (_df_fuels["BBL"] == bbl)]

    if ranking.empty and basic.empty and fuels.empty:
        return None

    # Merge on the fly; use the first available dataset as base
    if not ranking.empty:
        merged = ranking.copy()
    else:
        merged = pd.DataFrame({"BBL": [bbl], "Calendar Year": [year]})

    if not basic.empty:
        merged = pd.merge(merged, basic, on=["Calendar Year", "BBL"], how="outer")
    if not fuels.empty:
        merged = pd.merge(merged, fuels, on=["Calendar Year", "BBL"], how="outer")

    if merged.empty:
        return None

    row = merged.iloc[0]

    status_val = row.get("status", None)
    status_text, status_color = status_to_text(status_val)

    return BuildingInfo(
        bbl=int(row["BBL"]),
        calendar_year=int(row["Calendar Year"]),
        property_name=row.get("Property Name") if pd.notna(row.get("Property Name")) else None,
        address=row.get("address") if pd.notna(row.get("address")) else None,
        address_1=row.get("Address 1") if pd.notna(row.get("Address 1")) else None,
        status=bool(status_val) if pd.notna(status_val) else False,
        status_text=status_text,
        status_color=status_color,
        ranking=int(row["ranking"]) if pd.notna(row.get("ranking")) else None,
        energy_star_score=to_float(row.get("ENERGY STAR Score"), None),
        largest_property_use_type_gross_floor_area_ft2=to_float(
            row.get("Largest Property Use Type - Gross Floor Area (ft²)"), None
        ),
        calculated_emissions=to_float(row.get("Emisiones Calculadas"), None),
        emissions_limit=to_float(row.get("Limite"), None),
        excess_emissions=to_float(row.get("Exceso"), None),
        difference=to_float(row.get("Diferencia"), None),
        relative_to_limit=to_float(row.get("Relativo"), None),
        dob_emissions=to_float(row.get("Emisiones DOB_y", row.get("Emisiones DOB_x")), None),
        penalty=to_float(row.get("multa"), None),
    )


def get_penalty_forecast(year: int, bbl: int) -> PenaltyForecast | None:
    """Return future penalty predictions for a building."""
    pred = _df_predictions[(_df_predictions["Calendar Year"] == year) & (_df_predictions["BBL"] == bbl)]
    if pred.empty:
        return None

    row = pred.iloc[0]
    return PenaltyForecast(
        calendar_year=int(row["Calendar Year"]),
        bbl=int(row["BBL"]),
        penalty_2030=max(to_float(row.get("multa 2030"), 0.0), 0.0),
        penalty_2035=max(to_float(row.get("multa 2035"), 0.0), 0.0),
        penalty_2040=max(to_float(row.get("multa 2040"), 0.0), 0.0),
    )


def get_fuel_breakdown(year: int, bbl: int) -> FuelBreakdown | None:
    """Return emissions breakdown by fuel type for a building."""
    fuels = _df_fuels_analysis[(_df_fuels_analysis["Calendar Year"] == year) & (_df_fuels_analysis["BBL"] == bbl)]
    if fuels.empty:
        return None

    row = fuels.iloc[0]
    return FuelBreakdown(
        calendar_year=int(row["Calendar Year"]),
        bbl=int(row["BBL"]),
        fuel_oil=max(to_float(row.get("Fuel Oil"), 0.0), 0.0),
        electricity=max(to_float(row.get("Electricity"), 0.0), 0.0),
        natural_gas=max(to_float(row.get("Natural Gas"), 0.0), 0.0),
        others=max(to_float(row.get("Others"), 0.0), 0.0),
    )


def get_future_consumption(bbl: int) -> list[FutureConsumptionScenario]:
    """Return future consumption scenarios for a building."""
    df_future = _df_future.copy()
    df_future["BBL"] = df_future["BBL"].astype(int)
    row = df_future[df_future["BBL"] == bbl]
    if row.empty:
        return []

    r = row.iloc[0]
    scenarios = []
    mapping = {
        "2030": ["low_2030", "med_2030", "high_2030"],
        "2035": ["low_2035", "med_2035", "high_2035"],
        "2040": ["low_2040", "med_2040", "high_2040"],
    }
    scenario_labels = ["Low", "Med", "High"]

    for year, cols in mapping.items():
        for label, col in zip(scenario_labels, cols):
            val = r.get(col)
            if pd.notna(val):
                scenarios.append(
                    FutureConsumptionScenario(
                        year=year,
                        scenario=label,
                        value=float(val),
                    )
                )

    return scenarios

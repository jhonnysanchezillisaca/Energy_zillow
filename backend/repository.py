import pandas as pd
from pathlib import Path
from typing import Optional

from backend.config import DATA_DIR
from backend.models import (
    BuildingInfo,
    BuildingSnapshot,
    FuelBreakdown,
    FutureConsumptionScenario,
    PenaltyForecast,
    SearchResult,
)
from backend.utils.helpers import normalize_text, status_to_text, to_float

from rapidfuzz import fuzz, process


class BuildingRepository:
    """
    Deep module: all building data access behind a small interface.
    Production loads from CSV; tests pass in-memory DataFrames directly.
    """

    @classmethod
    def from_csv(cls, data_dir: Path = DATA_DIR) -> "BuildingRepository":
        """Load all datasets from the committed data/ directory."""
        df_basic = pd.read_csv(data_dir / "basic_information.csv", low_memory=False)
        df_basic.columns = df_basic.columns.str.strip()

        df_fuels = pd.read_csv(data_dir / "fuels.csv", low_memory=False)
        df_fuels_analysis = pd.read_csv(data_dir / "fuels_analisis.csv", low_memory=False)
        df_predictions = pd.read_csv(data_dir / "predictions.csv", low_memory=False)
        df_ranking = pd.read_csv(data_dir / "ranking.csv", low_memory=False)
        df_future = pd.read_csv(data_dir / "pred_to_display.csv", low_memory=False)

        return cls(
            df_basic=df_basic,
            df_fuels=df_fuels,
            df_fuels_analysis=df_fuels_analysis,
            df_predictions=df_predictions,
            df_ranking=df_ranking,
            df_future=df_future,
        )

    def __init__(
        self,
        *,
        df_basic: pd.DataFrame,
        df_fuels: pd.DataFrame,
        df_fuels_analysis: pd.DataFrame,
        df_predictions: pd.DataFrame,
        df_ranking: pd.DataFrame,
        df_future: pd.DataFrame,
    ):
        self._df_basic = df_basic
        self._df_fuels = df_fuels
        self._df_fuels_analysis = df_fuels_analysis
        self._df_predictions = df_predictions
        self._df_ranking = df_ranking
        self._df_future = df_future

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_building_info(self, year: int, bbl: int) -> BuildingInfo | None:
        """Return combined building info from ranking, basic info, and fuels datasets."""
        ranking = self._df_ranking[
            (self._df_ranking["Calendar Year"] == year) & (self._df_ranking["BBL"] == bbl)
        ]
        basic = self._df_basic[
            (self._df_basic["Calendar Year"] == year) & (self._df_basic["BBL"] == bbl)
        ]
        fuels = self._df_fuels[
            (self._df_fuels["Calendar Year"] == year) & (self._df_fuels["BBL"] == bbl)
        ]

        if ranking.empty and basic.empty and fuels.empty:
            return None

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

    def get_penalty_forecast(self, year: int, bbl: int) -> PenaltyForecast | None:
        """Return future penalty predictions for a building."""
        pred = self._df_predictions[
            (self._df_predictions["Calendar Year"] == year) & (self._df_predictions["BBL"] == bbl)
        ]
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

    def get_fuel_breakdown(self, year: int, bbl: int) -> FuelBreakdown | None:
        """Return emissions breakdown by fuel type for a building."""
        fuels = self._df_fuels_analysis[
            (self._df_fuels_analysis["Calendar Year"] == year)
            & (self._df_fuels_analysis["BBL"] == bbl)
        ]
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

    def get_future_consumption(self, bbl: int) -> list[FutureConsumptionScenario]:
        """Return future consumption scenarios for a building."""
        df_future = self._df_future.copy()
        df_future["BBL"] = df_future["BBL"].astype(int)
        row = df_future[df_future["BBL"] == bbl]
        if row.empty:
            return []

        r = row.iloc[0]
        scenarios: list[FutureConsumptionScenario] = []
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

    def search_address(self, address: str) -> SearchResult | None:
        """
        Fuzzy-search a building by address across both 'address' and 'Address 1' columns.
        Returns the best match as a SearchResult, or None if no good match found.
        """
        if not address or not str(address).strip():
            return None

        if "address" not in self._df_basic.columns or "Address 1" not in self._df_basic.columns:
            raise ValueError("Missing 'address' or 'Address 1' columns in basic_information.csv")

        col1 = "address"
        col2 = "Address 1"

        addresses1 = self._df_basic[col1].fillna("").astype(str).tolist()
        addresses2 = self._df_basic[col2].fillna("").astype(str).tolist()

        norm1 = [normalize_text(a) for a in addresses1]
        norm2 = [normalize_text(a) for a in addresses2]
        norm_query = normalize_text(address)

        results1 = process.extract(norm_query, norm1, scorer=fuzz.WRatio, limit=5)
        results2 = process.extract(norm_query, norm2, scorer=fuzz.WRatio, limit=5)

        if not results1 and not results2:
            return None

        best1 = results1[0] if results1 else ("", -1, None)
        best2 = results2[0] if results2 else ("", -1, None)

        score1, idx1 = best1[1], best1[2]
        score2, idx2 = best2[1], best2[2]

        if score1 >= score2 and idx1 is not None:
            idx_final = idx1
            best_score = score1
        elif idx2 is not None:
            idx_final = idx2
            best_score = score2
        else:
            return None

        row = self._df_basic.iloc[idx_final]
        bbl = int(row["BBL"])

        matched_address = row.get("address") if score1 >= score2 else row.get("Address 1")
        if pd.isna(matched_address):
            matched_address = row.get("Address 1") if score1 >= score2 else row.get("address")

        return SearchResult(
            bbl=bbl,
            property_name=row.get("Property Name") if pd.notna(row.get("Property Name")) else None,
            address=matched_address if pd.notna(matched_address) else None,
            match_score=float(best_score),
        )

    # ------------------------------------------------------------------
    # Aggregate interface
    # ------------------------------------------------------------------

    def get_building_snapshot(self, year: int, bbl: int) -> BuildingSnapshot | None:
        """Assemble everything needed for recommendations in one call."""
        info = self.get_building_info(year, bbl)
        if info is None:
            return None
        penalties = self.get_penalty_forecast(year, bbl)
        fuels = self.get_fuel_breakdown(year, bbl)
        return BuildingSnapshot(info=info, penalties=penalties, fuels=fuels)


# ------------------------------------------------------------------------------
# Production singleton — lazily loaded so import-time I/O disappears.
# ------------------------------------------------------------------------------
_repo_instance: BuildingRepository | None = None


def get_repository() -> BuildingRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = BuildingRepository.from_csv()
    return _repo_instance

import os
from openai import OpenAI
from backend.config import OPENAI_API_KEY
from backend.models import RecommendationResponse
from backend.services.buildings import get_building_info, get_penalty_forecast, get_fuel_breakdown
from backend.utils.helpers import ensure_dict


def generate_recommendations(bbl: int) -> RecommendationResponse:
    """Generate 5 energy efficiency recommendations using OpenAI."""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)

    info = get_building_info(2024, bbl)
    penalties = get_penalty_forecast(2024, bbl)
    fuels = get_fuel_breakdown(2024, bbl)

    if info is None:
        raise ValueError(f"Building with BBL {bbl} not found.")

    prompt = f"""
    You are an expert building energy efficiency consultant.

    Based ONLY on the following building data, generate exactly 5 concrete improvement recommendations.
    The recommendations must be practical, specific, and related to emissions, penalties,
    fuels, ENERGY STAR, and regulatory compliance.

    Building data:
    - Name: {info.property_name or "N/A"}
    - Address: {info.address or info.address_1 or "N/A"}
    - Status: {info.status_text}
    - Ranking: {info.ranking if info.ranking is not None else "N/A"}
    - Year: {info.calendar_year}
    - Calculated emissions: {info.calculated_emissions if info.calculated_emissions is not None else "N/A"}
    - Emissions limit: {info.emissions_limit if info.emissions_limit is not None else "N/A"}
    - Excess emissions: {info.excess_emissions if info.excess_emissions is not None else "N/A"}
    - Difference: {info.difference if info.difference is not None else "N/A"}
    - Relative to limit: {info.relative_to_limit if info.relative_to_limit is not None else "N/A"}
    - Current penalty: {info.penalty if info.penalty is not None else "N/A"}
    - Estimated penalty 2030: {penalties.penalty_2030 if penalties else "N/A"}
    - Estimated penalty 2035: {penalties.penalty_2035 if penalties else "N/A"}
    - Estimated penalty 2040: {penalties.penalty_2040 if penalties else "N/A"}
    - ENERGY STAR Score: {info.energy_star_score if info.energy_star_score is not None else "N/A"}
    - Electricity: {fuels.electricity if fuels else "N/A"}
    - Natural Gas: {fuels.natural_gas if fuels else "N/A"}
    - Other fuels: {fuels.others if fuels else "N/A"}
    - Fuel Oil: {fuels.fuel_oil if fuels else "N/A"}

    The recommendations must include:
    - expected impact on emissions (% or qualitative)
    - relation to penalties reduction
    - level of investment (low, medium, high)
    - implementation difficulty

    Return the answer in English, as a numbered list from 1 to 5.
    Do not invent data. If any data is missing, use what is available.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in building energy efficiency and decarbonization."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return RecommendationResponse(
        bbl=bbl,
        recommendations=response.choices[0].message.content,
    )

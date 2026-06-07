import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 2030, 2035, 2040 penalty predictions

if __name__ == "__main__":
    from core.emission_limits import get_emission_factor

    df = pd.read_csv("merged.csv", low_memory=False)

    df_test_fuels = df[["Calendar Year", "BBL",
                        "Fuel Oil #2 Use (kBtu)",
                        "Fuel Oil #4 Use (kBtu)",
                        "Fuel Oil #5 & 6 Use (kBtu)",
                        "Diesel #2 Use (kBtu)",
                        "Natural Gas Use (kBtu)",
                        "Electricity Use - Grid Purchase (kWh)",
                        "District Steam Use (kBtu)",
                        "Kerosene Use (kBtu)",
                        "Propane Use (kBtu)"]].copy()

    cols = ["BBL",
            "Fuel Oil #2 Use (kBtu)",
            "Fuel Oil #4 Use (kBtu)",
            "Fuel Oil #5 & 6 Use (kBtu)",
            "Diesel #2 Use (kBtu)",
            "Natural Gas Use (kBtu)",
            "Electricity Use - Grid Purchase (kWh)",
            "District Steam Use (kBtu)",
            "Kerosene Use (kBtu)",
            "Propane Use (kBtu)"]

    for col in cols:
        df_test_fuels[col] = pd.to_numeric(df_test_fuels[col].replace("Not Available", np.nan), errors='coerce')

    df_test_fuels = df_test_fuels.fillna(0)

    df_test_fuels["Emissions"] = (
        df_test_fuels["Fuel Oil #2 Use (kBtu)"] * 0.00007421 +
        df_test_fuels["Fuel Oil #4 Use (kBtu)"] * 0.00007529 +
        df_test_fuels["Fuel Oil #5 & 6 Use (kBtu)"] * 0.00007529 +
        df_test_fuels["Diesel #2 Use (kBtu)"] * 0.00007421 +
        df_test_fuels["Natural Gas Use (kBtu)"] * 0.00005311 +
        df_test_fuels["Electricity Use - Grid Purchase (kWh)"] * 0.000288962 +
        df_test_fuels["District Steam Use (kBtu)"] * 0.00004493 +
        df_test_fuels["Kerosene Use (kBtu)"] * 0.00007769 +
        df_test_fuels["Propane Use (kBtu)"] * 0.00006425
    )

    # Manual CO2 emissions calculation: feature * coefficient
    # Calculate maximum emissions

    df_emissions = df[
        ["Calendar Year", "BBL", "Largest Property Use Type - Gross Floor Area (ft²)", "Primary Property Type - Self Selected"]
    ].copy()

    # Calculate penalties for each target year
    for year in [2030, 2035, 2040]:
        df_emissions["Coefficient"] = df_emissions["Primary Property Type - Self Selected"].apply(
            lambda x: get_emission_factor(x, year))

        df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
            df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
        df_emissions = df_emissions.fillna(0)

        df_emissions["Limit"] = (
            df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"] * df_emissions["Coefficient"]
        )

        df_emissions["Excess"] = df_test_fuels["Emissions"] - df_emissions["Limit"]
        df_emissions[f"penalty_{year}"] = df_emissions["Excess"] * 268

    df_predictions = df_emissions[["Calendar Year", "BBL", "penalty_2030", "penalty_2035", "penalty_2040"]].copy()

    # Drop duplicates
    df_predictions.drop_duplicates(subset=["BBL", "Calendar Year"], inplace=True, ignore_index=False)

    # Fix negative penalties
    for year in [2030, 2035, 2040]:
        df_predictions[f'penalty_{year}'] = df_emissions[f'penalty_{year}'].apply(lambda x: max(x, 0))

    df_predictions.to_csv("predictions.csv", index=False, encoding="utf-8")

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

"""
This script uses merged.csv to compute fuel consumptions, emissions,
BBL, penalties, and exports fuels.csv and fuels_analisis.csv.
"""

if __name__ == "__main__":
    from core.emission_limits import get_emission_factor

    df = pd.read_csv("merged.csv", low_memory=False)

    # Create a subset with fuel columns
    df_test_fuels = df[["BBL",
                        "Fuel Oil #2 Use (kBtu)",
                        "Fuel Oil #4 Use (kBtu)",
                        "Fuel Oil #5 & 6 Use (kBtu)",
                        "Diesel #2 Use (kBtu)",
                        "Natural Gas Use (kBtu)",
                        "Electricity Use - Grid Purchase (kWh)",
                        "District Steam Use (kBtu)",
                        "Kerosene Use (kBtu)",
                        "Propane Use (kBtu)",
                        "Calendar Year"]].copy()

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

    # Manual CO2 emissions calculation: feature * coefficient
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

    # Calculate emissions limit and penalty
    df_emissions = df[
        ["Calendar Year", "BBL", "Largest Property Use Type - Gross Floor Area (ft²)", "Primary Property Type - Self Selected"]
    ].copy()

    year = 2024
    df_emissions["Coefficient"] = df_emissions["Primary Property Type - Self Selected"].apply(
        lambda x: get_emission_factor(x, year))

    df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"] = pd.to_numeric(
        df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"].replace("Not Available", np.nan), errors='coerce')
    df_emissions = df_emissions.fillna(0)

    df_emissions["Limit"] = (
        df_emissions["Largest Property Use Type - Gross Floor Area (ft²)"] * df_emissions["Coefficient"]
    )

    df_emissions["Excess"] = df_test_fuels["Emissions"] - df_emissions["Limit"]
    # Fix limit 0
    df_emissions.loc[df_emissions["Limit"] == 0, "Excess"] = 0
    df_emissions["Penalty"] = df_emissions["Excess"] * 268

    # Total emissions from DOB data
    df_total_emissions = df[["BBL", "Calendar Year", "Total (Location-Based) GHG Emissions (Metric Tons CO2e)"]].copy()
    df_total_emissions.rename(
        columns={"Total (Location-Based) GHG Emissions (Metric Tons CO2e)": "DOB Emissions"},
        inplace=True
    )
    df_total_emissions["Calculated Emissions"] = df_test_fuels["Emissions"]

    df_total_emissions["DOB Emissions"] = pd.to_numeric(df_total_emissions["DOB Emissions"], errors='coerce')
    df_total_emissions["Calculated Emissions"] = pd.to_numeric(df_total_emissions["Calculated Emissions"], errors='coerce')

    df_total_emissions["Difference"] = df_total_emissions["Calculated Emissions"] - df_total_emissions["DOB Emissions"]
    df_total_emissions["Relative"] = df_total_emissions["Difference"] / df_total_emissions["DOB Emissions"]
    df_total_emissions['Relative'] = df_total_emissions['Relative'].replace([np.inf, -np.inf], 0)

    # Fix relative calculation
    df_total_emissions['Relative'] = (
        (-df_emissions["Limit"] + df_total_emissions["Calculated Emissions"]) / df_emissions["Limit"]
    )
    df_total_emissions['Relative'] = df_total_emissions['Relative'].replace([np.inf, -np.inf], 0)

    # Fix negative penalties
    df_emissions['Penalty'] = df_emissions['Penalty'].apply(lambda x: max(x, 0))

    df_final = pd.merge(df_emissions, df_total_emissions, how='inner', on=['BBL', "Calendar Year"])

    df_final.drop('Largest Property Use Type - Gross Floor Area (ft²)', axis=1, inplace=True)
    df_final.drop('Primary Property Type - Self Selected', axis=1, inplace=True)
    df_final.drop('Coefficient', axis=1, inplace=True)

    # Compliance status: True means compliant with regulation
    df_final["status"] = df_final["Excess"] < 0

    # Round figures
    df_final["Limit"] = df_final["Limit"].round(0)
    df_final["Excess"] = df_final["Excess"].round(0)
    df_final["Penalty"] = df_final["Penalty"].round(0)
    df_final["DOB Emissions"] = df_final["DOB Emissions"].round(0)
    df_final["Calculated Emissions"] = df_final["Calculated Emissions"].round(0)
    df_final["Difference"] = df_final["Difference"].round(0)
    df_final["Relative"] = df_final["Relative"].round(3)

    # Create fuel consumption dataset for pie chart
    df_fuels_consumption = df_test_fuels.copy()
    df_fuels_consumption.drop('Emissions', axis=1, inplace=True)

    # Convert to tons of CO2
    df_fuels_consumption["Fuel Oil #2 Use (kBtu)"] = df_fuels_consumption["Fuel Oil #2 Use (kBtu)"] * 0.00007421
    df_fuels_consumption["Fuel Oil #4 Use (kBtu)"] = df_fuels_consumption["Fuel Oil #4 Use (kBtu)"] * 0.00007529
    df_fuels_consumption["Fuel Oil #5 & 6 Use (kBtu)"] = df_fuels_consumption["Fuel Oil #5 & 6 Use (kBtu)"] * 0.00007529
    df_fuels_consumption["Diesel #2 Use (kBtu)"] = df_fuels_consumption["Diesel #2 Use (kBtu)"] * 0.00007421
    df_fuels_consumption["Natural Gas Use (kBtu)"] = df_fuels_consumption["Natural Gas Use (kBtu)"] * 0.00005311
    df_fuels_consumption["Electricity Use - Grid Purchase (kWh)"] = df_fuels_consumption["Electricity Use - Grid Purchase (kWh)"] * 0.000288962
    df_fuels_consumption["District Steam Use (kBtu)"] = df_fuels_consumption["District Steam Use (kBtu)"] * 0.00004493
    df_fuels_consumption["Kerosene Use (kBtu)"] = df_fuels_consumption["Kerosene Use (kBtu)"] * 0.00007769
    df_fuels_consumption["Propane Use (kBtu)"] = df_fuels_consumption["Propane Use (kBtu)"] * 0.00006425

    # Create aggregated fuel columns
    df_fuels_consumption["Fuel Oil"] = (
        df_fuels_consumption["Fuel Oil #2 Use (kBtu)"] +
        df_fuels_consumption["Fuel Oil #4 Use (kBtu)"] +
        df_fuels_consumption["Fuel Oil #5 & 6 Use (kBtu)"]
    )
    df_fuels_consumption["Electricity"] = df_fuels_consumption["Electricity Use - Grid Purchase (kWh)"]
    df_fuels_consumption["Natural Gas"] = (
        df_fuels_consumption["Natural Gas Use (kBtu)"] + df_fuels_consumption["Propane Use (kBtu)"]
    )
    df_fuels_consumption["Others"] = (
        df_fuels_consumption["District Steam Use (kBtu)"] +
        df_fuels_consumption["Kerosene Use (kBtu)"] +
        df_fuels_consumption["Diesel #2 Use (kBtu)"]
    )

    # Drop original columns
    for col in [
        "Fuel Oil #2 Use (kBtu)", "Fuel Oil #4 Use (kBtu)", "Fuel Oil #5 & 6 Use (kBtu)",
        "Diesel #2 Use (kBtu)", "Natural Gas Use (kBtu)", "Electricity Use - Grid Purchase (kWh)",
        "District Steam Use (kBtu)", "Kerosene Use (kBtu)", "Propane Use (kBtu)"
    ]:
        df_fuels_consumption.drop(col, axis=1, inplace=True)

    # Save datasets
    df_final.drop_duplicates(subset=["BBL", "Calendar Year"], keep='first', inplace=True, ignore_index=False)
    df_fuels_consumption.drop_duplicates(subset=["BBL", "Calendar Year"], keep='first', inplace=True, ignore_index=False)

    df_fuels_consumption.to_csv("fuels_analisis.csv", index=False, encoding='utf-8')
    df_final.to_csv("fuels.csv", index=False, encoding='utf-8')

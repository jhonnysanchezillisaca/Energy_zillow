import pandas as pd

# Create normalized fuel price weights for future consumption predictions

if __name__ == "__main__":
    oil = pd.read_csv("oil_forecast.csv")
    gas = pd.read_csv("gas_forecast.csv")
    electricity = pd.read_csv("electricity_forecast.csv")

    # 2024 baseline prices
    oil_2024 = 4   # $/gal
    gas_2024 = 15  # $/MMBtu
    electricity_2024 = 0.25  # $/kWh

    # Target years
    years = [2030, 2035, 2040]

    # Filter target years
    df_oil = oil[oil["year"].isin(years)]
    df_gas = gas[gas["year"].isin(years)]
    df_electricity = electricity[electricity["year"].isin(years)]

    # Normalize with respect to 2024
    df_oil["normalized_price_oil_low"] = (df_oil["lower_dollars_per_gallon"] - oil_2024) / oil_2024
    df_oil["normalized_price_oil_med"] = (df_oil["predicted_dollars_per_gallon"] - oil_2024) / oil_2024
    df_oil["normalized_price_oil_high"] = (df_oil["upper_dollars_per_gallon"] - oil_2024) / oil_2024

    df_gas["normalized_price_gas_low"] = (df_gas["lower_dollars_per_mcf"] - gas_2024) / gas_2024
    df_gas["normalized_price_gas_med"] = (df_gas["predicted_dollars_per_mcf"] - gas_2024) / gas_2024
    df_gas["normalized_price_gas_high"] = (df_gas["upper_dollars_per_mcf"] - gas_2024) / gas_2024

    df_electricity["normalized_price_electricity_low"] = (df_electricity["lower_cents_per_kwh"] / 100 - electricity_2024) / electricity_2024
    df_electricity["normalized_price_electricity_med"] = (df_electricity["predicted_cents_per_kwh"] / 100 - electricity_2024) / electricity_2024
    df_electricity["normalized_price_electricity_high"] = (df_electricity["upper_cents_per_kwh"] / 100 - electricity_2024) / electricity_2024

    # Drop original columns
    df_oil = df_oil.drop(columns=["predicted_dollars_per_gallon", "lower_dollars_per_gallon", "upper_dollars_per_gallon"])
    df_gas = df_gas.drop(columns=["predicted_dollars_per_mcf", "lower_dollars_per_mcf", "upper_dollars_per_mcf"])
    df_electricity = df_electricity.drop(
        columns=["predicted_dollars_per_kwh", "lower_cents_per_kwh", "upper_cents_per_kwh", "predicted_cents_per_kwh"]
    )

    # Merge dataframes
    df = pd.merge(df_oil, df_gas, on="year")
    df = pd.merge(df, df_electricity, on="year")

    # Save result
    df.to_csv("weights_fuels.csv", index=False)

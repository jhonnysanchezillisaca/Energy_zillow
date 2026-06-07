# Program to calculate fuel prices by year
# Starting with electricity in NY, USA

# pip install pandas requests matplotlib prophet

import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet


def get_eia_monthly_prices_ny(api_key, sector="RES", state="NY"):
    """
    Download monthly electricity prices from EIA.
    Default: New York, residential sector.

    Returns:
        DataFrame with columns: ds, y
        ds = monthly date
        y = price in cents/kWh
    """
    url = "https://api.eia.gov/v2/electricity/retail-sales/data/"

    params = {
        "api_key": api_key,
        "frequency": "monthly",
        "data[]": "price",
        "facets[stateid][]": state,
        "facets[sectorid][]": sector,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()["response"]["data"]

    df = pd.DataFrame(data)

    df = df[["period", "price"]].copy()
    df["ds"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["price"])

    df = df[["ds", "y"]].dropna()
    df = df.sort_values("ds")

    return df


def forecast_annual_kwh_price(api_key, years=15, sector="RES", state="NY"):
    """
    Train Prophet with monthly data and return annual prediction
    for the next `years` years.

    Returns:
        forecast_annual: DataFrame with:
            year
            predicted_cents_per_kwh
            predicted_dollars_per_kwh
            lower_cents_per_kwh
            upper_cents_per_kwh
    """

    df = get_eia_monthly_prices_ny(
        api_key=api_key,
        sector=sector,
        state=state
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )

    model.fit(df)

    future = model.make_future_dataframe(
        periods=years * 12,
        freq="MS"
    )

    forecast = model.predict(future)

    forecast_future = forecast[forecast["ds"] > df["ds"].max()].copy()
    forecast_future["year"] = forecast_future["ds"].dt.year

    forecast_annual = (
        forecast_future
        .groupby("year")
        .agg(
            predicted_cents_per_kwh=("yhat", "mean"),
            lower_cents_per_kwh=("yhat_lower", "mean"),
            upper_cents_per_kwh=("yhat_upper", "mean"),
        )
        .reset_index()
        .head(years)
    )

    forecast_annual["predicted_dollars_per_kwh"] = (
        forecast_annual["predicted_cents_per_kwh"] / 100
    )

    return forecast_annual, model, forecast, df


def plot_annual_forecast(forecast_annual):
    """
    Plot the annual average electricity price prediction.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        forecast_annual["year"],
        forecast_annual["predicted_cents_per_kwh"],
        marker="o",
        label="Prediction"
    )

    plt.fill_between(
        forecast_annual["year"],
        forecast_annual["lower_cents_per_kwh"],
        forecast_annual["upper_cents_per_kwh"],
        alpha=0.2,
        label="Uncertainty interval"
    )

    plt.title("Annual Average Electricity Price Prediction in NY")
    plt.xlabel("Year")
    plt.ylabel("Average Price, cents/kWh")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Error: EIA_API_KEY environment variable is not set.")
        print("Set it with: export EIA_API_KEY=your_key_here")
        exit(1)

    df_pred, model, forecast_monthly, historical_df = forecast_annual_kwh_price(
        api_key=api_key,
        years=15,
        sector="RES",
        state="NY"
    )

    print(df_pred)

    df_pred.to_csv("electricity_forecast.csv", index=False)

    # plot_annual_forecast(df_pred)

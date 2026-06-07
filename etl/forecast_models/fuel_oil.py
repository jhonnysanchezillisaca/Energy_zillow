import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet


def get_eia_heating_oil_prices(api_key):
    """
    Download weekly residential heating oil prices for New York from EIA.

    Unit:
        dollars per gallon
    """

    url = "https://api.eia.gov/v2/petroleum/pri/wfr/data/"

    params = {
        "api_key": api_key,
        "frequency": "weekly",
        "data[]": "value",
        "facets[series][]": "W_EPD2F_PRS_SNY_DPG",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 10000,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.text)
        response.raise_for_status()

    data = response.json()["response"]["data"]

    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("The API returned no data. Check the API key or series code.")

    df = df[["period", "value"]].copy()
    df["ds"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[["ds", "y"]].dropna().sort_values("ds")

    return df


def forecast_annual_heating_oil_price(api_key, years=15):
    """
    Train Prophet with weekly heating oil prices
    and return the average annual prediction for upcoming years.
    """

    df = get_eia_heating_oil_prices(api_key)

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )

    model.fit(df)

    future = model.make_future_dataframe(
        periods=years * 52,
        freq="W"
    )

    forecast = model.predict(future)

    last_date = df["ds"].max()
    last_year = df["ds"].dt.year.max()

    forecast_future = forecast[forecast["ds"] > last_date].copy()
    forecast_future["year"] = forecast_future["ds"].dt.year

    forecast_annual = (
        forecast_future
        .groupby("year")
        .agg(
            predicted_dollars_per_gallon=("yhat", "mean"),
            lower_dollars_per_gallon=("yhat_lower", "mean"),
            upper_dollars_per_gallon=("yhat_upper", "mean"),
        )
        .reset_index()
    )

    forecast_annual = forecast_annual[
        forecast_annual["year"] > last_year
    ].head(years)

    return forecast_annual, model, forecast, df


def plot_heating_oil_forecast(forecast_annual):
    """
    Plot the annual heating oil price prediction.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        forecast_annual["year"],
        forecast_annual["predicted_dollars_per_gallon"],
        marker="o",
        label="Prediction"
    )

    plt.fill_between(
        forecast_annual["year"],
        forecast_annual["lower_dollars_per_gallon"],
        forecast_annual["upper_dollars_per_gallon"],
        alpha=0.2,
        label="Uncertainty interval"
    )

    plt.title("Annual Heating Oil Price Prediction - New York")
    plt.xlabel("Year")
    plt.ylabel("$/gallon")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Error: EIA_API_KEY environment variable is not set.")
        print("Set it with: export EIA_API_KEY=your_key_here")
        exit(1)

    df_oil_pred, oil_model, oil_forecast_weekly, oil_historical_df = (
        forecast_annual_heating_oil_price(
            api_key=api_key,
            years=15
        )
    )

    print("Last historical data point:")
    print(oil_historical_df["ds"].max())

    print("\nAnnual prediction:")
    print(df_oil_pred)

    df_oil_pred.to_csv("oil_forecast.csv", index=False)

    # plot_heating_oil_forecast(df_oil_pred)

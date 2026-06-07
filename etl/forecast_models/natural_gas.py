import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet


def get_eia_monthly_natural_gas_prices_ny(
    api_key,
    area="SNY",
    process="PRS"
):
    """
    Download monthly natural gas prices from EIA.

    Default:
        area="SNY"      -> New York
        process="PRS"   -> Price Delivered to Residential Consumers

    Returns:
        DataFrame with columns:
            ds = monthly date
            y  = price in dollars per thousand cubic feet
    """

    url = "https://api.eia.gov/v2/natural-gas/pri/sum/data/"

    params = {
        "api_key": api_key,
        "frequency": "monthly",
        "data[]": "value",
        "facets[duoarea][]": area,
        "facets[process][]": process,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()["response"]["data"]

    df = pd.DataFrame(data)

    df = df[["period", "value"]].copy()
    df["ds"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[["ds", "y"]].dropna()
    df = df.sort_values("ds")

    return df


def forecast_annual_natural_gas_price(
    api_key,
    years=15,
    area="SNY",
    process="PRS"
):
    """
    Train Prophet with monthly natural gas prices
    and return the average annual prediction for upcoming years.

    Returns:
        forecast_annual
        model
        forecast_monthly
        historical_df
    """

    df = get_eia_monthly_natural_gas_prices_ny(
        api_key=api_key,
        area=area,
        process=process
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
            predicted_dollars_per_mcf=("yhat", "mean"),
            lower_dollars_per_mcf=("yhat_lower", "mean"),
            upper_dollars_per_mcf=("yhat_upper", "mean"),
        )
        .reset_index()
        .head(years)
    )

    return forecast_annual, model, forecast, df


def plot_annual_natural_gas_forecast(forecast_annual):
    """
    Plot the annual average natural gas price prediction.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        forecast_annual["year"],
        forecast_annual["predicted_dollars_per_mcf"],
        marker="o",
        label="Prediction"
    )

    plt.fill_between(
        forecast_annual["year"],
        forecast_annual["lower_dollars_per_mcf"],
        forecast_annual["upper_dollars_per_mcf"],
        alpha=0.2,
        label="Uncertainty interval"
    )

    plt.title("Annual Average Natural Gas Price Prediction in NY")
    plt.xlabel("Year")
    plt.ylabel("Average Price, $/Mcf")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        print("Error: EIA_API_KEY environment variable is not set.")
        print("Set it with: export EIA_API_KEY=your_key_here")
        exit(1)

    df_gas_pred, gas_model, gas_forecast_monthly, gas_historical_df = (
        forecast_annual_natural_gas_price(
            api_key=api_key,
            years=15
        )
    )

    print(df_gas_pred)

    df_gas_pred.to_csv("gas_forecast.csv", index=False)

    # plot_annual_natural_gas_forecast(df_gas_pred)

import pandas as pd

# Future consumption budget expectations based on fuel price fluctuations

if __name__ == "__main__":
    df_w = pd.read_csv("weights_fuels.csv")
    df = pd.read_csv("fuels_analisis.csv")

    # Create weights
    df = df[df["Calendar Year"] == 2024]

    df["Total"] = df["Fuel Oil"] + df["Electricity"] + df["Natural Gas"]

    df["Fuel Oil"] = df["Fuel Oil"] / df["Total"]
    df["Electricity"] = df["Electricity"] / df["Total"]
    df["Natural Gas"] = df["Natural Gas"] / df["Total"]
    df = df.drop(columns=["Total"])

    df_building = df[["BBL", "Fuel Oil", "Electricity", "Natural Gas"]].copy()
    df_building = df_building.drop_duplicates(subset=["BBL"], keep="first")
    df_building = df_building.dropna(subset=["Fuel Oil"])

    rows, _ = df_building.shape

    # Oil operation (matrix multiplication with price weights)
    columns = ["BBL",
               "low_2030", "med_2030", "high_2030",
               "low_2035", "med_2035", "high_2035",
               "low_2040", "med_2040", "high_2040"]

    df_final = pd.DataFrame(columns=columns)

    for k in range(rows):
        row1 = df_building.iloc[k, 1:4].to_numpy()

        row21 = df_w.iloc[0, [1, 4, 7]].to_numpy()
        row22 = df_w.iloc[0, [2, 5, 8]].to_numpy()
        row23 = df_w.iloc[0, [3, 6, 9]].to_numpy()

        var_low_2030 = (row1 * row21).sum()
        var_med_2030 = (row1 * row22).sum()
        var_high_2030 = (row1 * row23).sum()

        row31 = df_w.iloc[1, [1, 4, 7]].to_numpy()
        row32 = df_w.iloc[1, [2, 5, 8]].to_numpy()
        row33 = df_w.iloc[1, [3, 6, 9]].to_numpy()

        var_low_2035 = (row1 * row31).sum()
        var_med_2035 = (row1 * row32).sum()
        var_high_2035 = (row1 * row33).sum()

        row41 = df_w.iloc[2, [1, 4, 7]].to_numpy()
        row42 = df_w.iloc[2, [2, 5, 8]].to_numpy()
        row43 = df_w.iloc[2, [3, 6, 9]].to_numpy()

        var_low_2040 = (row1 * row41).sum()
        var_med_2040 = (row1 * row42).sum()
        var_high_2040 = (row1 * row43).sum()

        df_final.loc[len(df_final)] = [
            df_building.iloc[k, 0],
            var_low_2030, var_med_2030, var_high_2030,
            var_low_2035, var_med_2035, var_high_2035,
            var_low_2040, var_med_2040, var_high_2040
        ]

    df_final.to_csv("pred_to_display.csv", index=False, encoding='utf-8')

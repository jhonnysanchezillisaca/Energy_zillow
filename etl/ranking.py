import pandas as pd
import numpy as np

# Ranking computation

if __name__ == "__main__":
    # 1. Load and initial cleanup
    df = pd.read_csv("merged.csv", low_memory=False)
    df_fuels = pd.read_csv("fuels.csv", low_memory=False)

    # 2. Prepare ranking data (keep one record per BBL, e.g. most recent year)
    df_ranking = df[["BBL", "ENERGY STAR Score", "Calendar Year"]].copy()
    df_ranking["ENERGY STAR Score"] = pd.to_numeric(
        df_ranking["ENERGY STAR Score"].replace("Not Available", np.nan), errors='coerce'
    )

    # 3. Prepare fuels data
    df_fuels1 = df_fuels[["Calendar Year", "BBL", "DOB Emissions"]].copy()

    # 4. Merge (will be 1-to-1, max ~72k rows)
    df_ranking_final = pd.merge(df_ranking, df_fuels1, on=["BBL", "Calendar Year"], how="inner")

    # 5. Compute ranking
    df_ranking_final["ranking1"] = df_ranking_final["ENERGY STAR Score"].rank(ascending=False, method='min')
    df_ranking_final["ranking2"] = df_ranking_final["DOB Emissions"].rank(ascending=True, method='min')

    df_ranking_final["score"] = df_ranking_final["ranking1"] + df_ranking_final["ranking2"]
    df_ranking_final["ranking"] = df_ranking_final["score"].rank(ascending=True, method='dense').astype('Int64')

    # Clean before export
    df_ranking_final.drop(columns=["ranking1", "ranking2", "score"], inplace=True)
    df_ranking_final.drop_duplicates(subset=["BBL", "Calendar Year"], inplace=True)

    # Export dataset
    df_ranking_final.to_csv("ranking.csv", index=False, encoding='utf-8')

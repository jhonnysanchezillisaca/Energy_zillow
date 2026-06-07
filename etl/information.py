import pandas as pd

"""
Creates a CSV with basic building information.
"""

if __name__ == "__main__":
    df = pd.read_csv("merged.csv", low_memory=False)

    df_basic = df[[
        "Calendar Year",
        "BBL",
        "Address 1",
        "address",
        "Property Name",
        "Largest Property Use Type - Gross Floor Area (ft²)"
    ]].copy()

    df_basic.drop_duplicates(subset=["BBL", "Calendar Year"], inplace=True)
    df_basic.to_csv("basic_information.csv", index=False, encoding='utf-8')

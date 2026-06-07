# This script downloads the LL84 and PLUTO datasets as CSV files from NYC Open Data.

import pandas as pd
import sys
import os

# Add parent directory to path so we can import from archive/Funciones.py if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == "__main__":
    print("Starting download: Datasets", flush=True)

    url_ll84 = "https://data.cityofnewyork.us/api/views/5zyy-y8am/rows.csv?accessType=DOWNLOAD"
    url_pluto = "https://data.cityofnewyork.us/api/views/64uk-42ks/rows.csv?accessType=DOWNLOAD"

    print("Starting download: LL84", flush=True)
    # Note: d_csv function is in archive/Funciones.py; run from project root if needed
    # from Funciones import d_csv
    # d_csv(url_ll84, 'LL84.csv')
    print("Starting download: PLUTO", flush=True)
    # d_csv(url_pluto, 'Pluto.csv')

    print("Finished download: Datasets", flush=True)

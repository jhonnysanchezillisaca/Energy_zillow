import pandas as pd
from rapidfuzz import process, fuzz
from backend.config import BASIC_INFO_CSV
from backend.models import SearchResult
from backend.utils.helpers import normalize_text


# Load once at module import for fast repeated lookups
_df_basic = pd.read_csv(BASIC_INFO_CSV)
_df_basic.columns = _df_basic.columns.str.strip()


def search_building(address: str) -> SearchResult | None:
    """
    Fuzzy-search a building by address across both 'address' and 'Address 1' columns.
    Returns the best match as a SearchResult, or None if no good match found.
    """
    if not address or not str(address).strip():
        return None

    if "address" not in _df_basic.columns or "Address 1" not in _df_basic.columns:
        raise ValueError("Missing 'address' or 'Address 1' columns in basic_information.csv")

    col1 = "address"
    col2 = "Address 1"

    addresses1 = _df_basic[col1].fillna("").astype(str).tolist()
    addresses2 = _df_basic[col2].fillna("").astype(str).tolist()

    norm1 = [normalize_text(a) for a in addresses1]
    norm2 = [normalize_text(a) for a in addresses2]
    norm_query = normalize_text(address)

    results1 = process.extract(norm_query, norm1, scorer=fuzz.WRatio, limit=5)
    results2 = process.extract(norm_query, norm2, scorer=fuzz.WRatio, limit=5)

    if not results1 and not results2:
        return None

    best1 = results1[0] if results1 else ("", -1, None)
    best2 = results2[0] if results2 else ("", -1, None)

    score1, idx1 = best1[1], best1[2]
    score2, idx2 = best2[1], best2[2]

    if score1 >= score2 and idx1 is not None:
        idx_final = idx1
        best_score = score1
    elif idx2 is not None:
        idx_final = idx2
        best_score = score2
    else:
        return None

    row = _df_basic.iloc[idx_final]
    bbl = int(row["BBL"])

    # Prefer the matched address column for display
    matched_address = row.get("address") if score1 >= score2 else row.get("Address 1")
    if pd.isna(matched_address):
        matched_address = row.get("Address 1") if score1 >= score2 else row.get("address")

    return SearchResult(
        bbl=bbl,
        property_name=row.get("Property Name") if pd.notna(row.get("Property Name")) else None,
        address=matched_address if pd.notna(matched_address) else None,
        match_score=float(best_score),
    )

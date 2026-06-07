import pandas as pd


def normalize_text(s: str) -> str:
    """Normalize address strings for fuzzy matching."""
    s = str(s).lower().strip()
    s = s.replace("avenue", "ave")
    s = s.replace("street", "st")
    s = s.replace("road", "rd")
    s = s.replace("boulevard", "blvd")
    return s


def to_float(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def to_int(value, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def format_money(value) -> str:
    return f"${to_int(value):,}"


def format_percent(value) -> str:
    return f"{round(to_float(value) * 100, 2)}%"


def status_to_text(status_raw):
    """Convert boolean compliance status to display text and color."""
    valor = str(status_raw).strip().lower()
    if valor == "true":
        return "Compliant", "green"
    elif valor == "false":
        return "Non-Compliant", "red"
    return "N/A", "gray"


def ensure_series(resultado):
    """
    Convert search results to a single pandas Series.
    Supports pd.Series, pd.DataFrame (first row), and dict.
    """
    if resultado is None:
        return None
    if isinstance(resultado, pd.Series):
        return resultado
    if isinstance(resultado, pd.DataFrame):
        if resultado.empty:
            return None
        return resultado.iloc[0]
    if isinstance(resultado, dict):
        return pd.Series(resultado)
    return None


def ensure_dict(resultado):
    """Convert search results to a native Python dict."""
    if resultado is None:
        return {}
    if isinstance(resultado, pd.Series):
        return resultado.fillna("").to_dict()
    if isinstance(resultado, pd.DataFrame):
        if resultado.empty:
            return {}
        return resultado.iloc[0].fillna("").to_dict()
    if isinstance(resultado, dict):
        return resultado
    return {}

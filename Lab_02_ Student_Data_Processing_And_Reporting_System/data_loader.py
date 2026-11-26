"""
data_loader.py
==============
Handles loading CSV files into Pandas DataFrames and constructing
DataFrames from lists of dictionaries.
"""

from typing import Dict, List, Optional
import pandas as pd


# ---------------------------------------------------------------------------
# Required column sets for validation
# ---------------------------------------------------------------------------
STUDENT_REQUIRED_COLS = {
    "student_id", "name", "department", "gender",
    "maths", "science", "english", "attendance_pct", "city",
}

SALES_REQUIRED_COLS = {
    "order_id", "product", "category", "region",
    "quantity", "unit_price", "order_date",
}

DEPT_REQUIRED_COLS = {"department", "HOD", "building"}


def load_csv(
    path: str,
    required_cols: Optional[set] = None,
    verbose: bool = True,
) -> Optional[pd.DataFrame]:
    """Load a CSV file into a Pandas DataFrame with robust error handling.

    Parameters
    ----------
    path : str
        File path to the CSV file.
    required_cols : set, optional
        Set of column names that must be present. Missing columns are
        reported but do NOT raise an exception.
    verbose : bool
        When True, print shape, columns, dtypes, and first 5 rows.

    Returns
    -------
    pd.DataFrame or None
        Returns a DataFrame copy so the caller cannot mutate the loaded
        data by accident.  Returns None if the file cannot be read.
    """
    df: Optional[pd.DataFrame] = None

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"[ERROR] File not found: '{path}'")
        print("        Please ensure the file exists at the specified path.")
        return None
    except pd.errors.EmptyDataError:
        print(f"[ERROR] File is empty: '{path}'")
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Could not read '{path}': {exc}")
        return None

    # --- column validation ---------------------------------------------------
    if required_cols:
        actual_lower = {c.lower() for c in df.columns}
        required_lower = {c.lower() for c in required_cols}
        missing = required_lower - actual_lower
        if missing:
            print(
                f"[WARNING] Missing expected column(s) in '{path}': "
                f"{sorted(missing)}"
            )
            print("          Processing will continue with available columns.")

    # --- display summary -----------------------------------------------------
    if verbose:
        _display_load_summary(df, path)

    return df.copy()


def _display_load_summary(df: pd.DataFrame, path: str) -> None:
    """Print a formatted summary of the loaded DataFrame."""
    separator = "-" * 60
    print(f"\n{separator}")
    print(f"  LOADED: {path}")
    print(separator)
    print(f"  Shape   : {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Columns : {list(df.columns)}")
    print("\n  Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<20} {dtype}")
    print("\n  First 5 Rows:")
    print(df.head(5).to_string(index=True))
    print(separator)


def dataframe_from_dicts(
    records: List[Dict],
    required_cols: Optional[set] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Build a Pandas DataFrame from a list of dictionaries.

    Parameters
    ----------
    records : list of dict
        Each dict represents one row; keys become column names.
    required_cols : set, optional
        Expected columns to validate against.
    verbose : bool
        When True, print a load summary.

    Returns
    -------
    pd.DataFrame
        A fresh copy of the constructed DataFrame.
    """
    if not records:
        print("[WARNING] Empty record list supplied – returning empty DataFrame.")
        return pd.DataFrame()

    df = pd.DataFrame(records)

    if required_cols:
        actual_lower = {c.lower() for c in df.columns}
        required_lower = {c.lower() for c in required_cols}
        missing = required_lower - actual_lower
        if missing:
            print(
                f"[WARNING] Missing expected column(s): {sorted(missing)}"
            )

    if verbose:
        _display_load_summary(df, "<in-memory list of dicts>")

    return df.copy()

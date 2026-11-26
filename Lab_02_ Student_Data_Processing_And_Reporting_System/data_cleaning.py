"""
data_cleaning.py
================
Data-cleaning utilities for student and sales DataFrames.
All operations are performed on copies; original DataFrames are never mutated.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd


# ---------------------------------------------------------------------------
# Column metadata
# ---------------------------------------------------------------------------

#: Student numeric columns (must be in [0, 100])
STUDENT_MARK_COLS: Tuple[str, ...] = ("maths", "science", "english")

#: Student numeric columns with custom valid ranges: col → (min, max)
STUDENT_NUMERIC_RANGES: Dict[str, Tuple[float, float]] = {
    "maths":          (0.0, 100.0),
    "science":        (0.0, 100.0),
    "english":        (0.0, 100.0),
    "attendance_pct": (0.0, 100.0),
}

#: Sales numeric columns with custom valid ranges
SALES_NUMERIC_RANGES: Dict[str, Tuple[float, float]] = {
    "quantity":   (0, float("inf")),
    "unit_price": (0.0, float("inf")),
}

#: Student text columns (stripped + title-cased)
STUDENT_TEXT_COLS: Tuple[str, ...] = ("name", "department", "gender", "city")

#: Sales text columns
SALES_TEXT_COLS: Tuple[str, ...] = ("product", "category", "region")

#: ID column per dataset
STUDENT_ID_COL: str = "student_id"
SALES_ID_COL: str = "order_id"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def missing_report(df: pd.DataFrame, label: str = "DataFrame") -> Dict[str, int]:
    """Report missing value counts per column.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to inspect.
    label : str
        A human-readable label printed in the output.

    Returns
    -------
    dict
        Mapping of column name → missing count (only columns with > 0 missing).
    """
    missing = df.isnull().sum()
    report = {col: int(cnt) for col, cnt in missing.items() if cnt > 0}

    separator = "-" * 55
    print(f"\n{separator}")
    print(f"  MISSING VALUE REPORT  --  {label}")
    print(separator)
    if report:
        for col, cnt in report.items():
            pct = cnt / len(df) * 100 if len(df) > 0 else 0.0
            print(f"  {col:<22} : {cnt:>4} missing  ({pct:5.1f}%)")
    else:
        print("  No missing values detected.")
    print(separator)
    return report


def clean_data(
    df: pd.DataFrame,
    dataset_type: str = "student",
    num_strategy: str = "median",
    text_strategy: str = "Unknown",
) -> Tuple[pd.DataFrame, Dict]:
    """Full cleaning pipeline: validate → standardise text → deduplicate → impute.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame (not mutated; a copy is returned).
    dataset_type : str
        ``"student"`` or ``"sales"`` — selects the correct range/column maps.
    num_strategy : str
        How to fill missing numeric values: ``"mean"``, ``"median"``, or ``"zero"``.
    text_strategy : str
        Fill value for missing text cells or ``"drop"`` to remove those rows.

    Returns
    -------
    (pd.DataFrame, dict)
        Cleaned DataFrame and a summary dictionary for reporting.
    """
    df = df.copy()

    rows_before = len(df)
    missing_before = int(df.isnull().sum().sum())

    # -- select column maps based on dataset type ----------------------------
    if dataset_type == "student":
        numeric_ranges = STUDENT_NUMERIC_RANGES
        text_cols = [c for c in STUDENT_TEXT_COLS if c in df.columns]
        id_col = STUDENT_ID_COL if STUDENT_ID_COL in df.columns else None
    else:
        numeric_ranges = SALES_NUMERIC_RANGES
        text_cols = [c for c in SALES_TEXT_COLS if c in df.columns]
        id_col = SALES_ID_COL if SALES_ID_COL in df.columns else None

    # -- Step 1: standardise text columns ------------------------------------
    text_fixes = _standardise_text(df, text_cols)

    # -- Step 2: coerce numeric columns, flag out-of-range as NaN ------------
    invalid_counts = _coerce_and_range_check(df, numeric_ranges)

    # -- Step 3: remove exact duplicate rows ---------------------------------
    exact_dups = int(df.duplicated().sum())
    df = df.drop_duplicates(keep="first")

    # -- Step 4: handle duplicate IDs (keep first, record conflicts) ---------
    id_conflicts: List[Dict] = []
    id_dup_count = 0
    if id_col:
        id_conflicts, id_dup_count = _handle_id_duplicates(df, id_col)
        df = df.drop_duplicates(subset=[id_col], keep="first")

    # -- Step 5: impute missing numeric values --------------------------------
    numeric_cols = [c for c in numeric_ranges.keys() if c in df.columns]
    numeric_imputed = _impute_numeric(df, numeric_cols, num_strategy)

    # -- Step 6: impute or drop missing text values --------------------------
    text_imputed = _impute_text(df, text_cols, text_strategy)

    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())

    summary = {
        "rows_before":        rows_before,
        "rows_after":         rows_after,
        "exact_dups_removed": exact_dups,
        "id_dup_removed":     id_dup_count,
        "id_conflicts":       id_conflicts,
        "missing_before":     missing_before,
        "missing_after":      missing_after,
        "invalid_values":     invalid_counts,
        "text_fixes":         text_fixes,
        "numeric_imputed":    numeric_imputed,
        "text_imputed":       text_imputed,
        "num_strategy":       num_strategy,
        "text_strategy":      text_strategy,
    }

    _print_cleaning_summary(summary)
    return df, summary


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _standardise_text(df: pd.DataFrame, text_cols: List[str]) -> int:
    """Strip whitespace and apply title-case to text columns in-place.

    Returns the number of cells modified.
    """
    fixes = 0
    for col in text_cols:
        if col not in df.columns:
            continue
        original = df[col].copy()
        df[col] = df[col].astype(str).str.strip().str.title()
        # Replace 'Nan' string artefacts back to NaN
        df[col] = df[col].replace("Nan", pd.NA)
        changed = (original.astype(str) != df[col].astype(str)).sum()
        fixes += int(changed)
    return fixes


def _coerce_and_range_check(
    df: pd.DataFrame,
    numeric_ranges: Dict[str, Tuple[float, float]],
) -> Dict[str, int]:
    """Coerce non-numeric values and out-of-range values to NaN in-place.

    Returns a dict of column → count of values replaced with NaN.
    """
    invalid: Dict[str, int] = {}
    for col, (lo, hi) in numeric_ranges.items():
        if col not in df.columns:
            continue
        original_nulls = df[col].isnull().sum()
        # Coerce non-numeric to NaN
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Mark out-of-range as NaN
        out_of_range = df[col].notna() & ~df[col].between(lo, hi)
        df.loc[out_of_range, col] = float("nan")
        new_nulls = df[col].isnull().sum()
        count = int(new_nulls - original_nulls)
        if count > 0:
            invalid[col] = count
    return invalid


def _handle_id_duplicates(
    df: pd.DataFrame, id_col: str
) -> Tuple[List[Dict], int]:
    """Find duplicate IDs, compare their rows, and record conflicts.

    Returns (list_of_conflict_dicts, count_of_duplicates_found).
    """
    dup_mask = df.duplicated(subset=[id_col], keep=False)
    dup_df = df[dup_mask]
    conflicts: List[Dict] = []

    for id_val, group in dup_df.groupby(id_col):
        rows = group.to_dict(orient="records")
        # Detect if any non-ID column differs across the duplicate rows
        non_id_cols = [c for c in df.columns if c != id_col]
        conflict_cols = []
        for col in non_id_cols:
            vals = {str(r.get(col)) for r in rows}
            if len(vals) > 1:
                conflict_cols.append(col)
        conflicts.append({
            "id": id_val,
            "count": len(rows),
            "conflicting_cols": conflict_cols,
        })

    total_extra = int(df.duplicated(subset=[id_col], keep="first").sum())
    return conflicts, total_extra


def _impute_numeric(
    df: pd.DataFrame,
    numeric_cols: List[str],
    strategy: str,
) -> int:
    """Fill NaN in numeric columns according to strategy.

    Returns the number of cells filled.
    """
    filled = 0
    for col in numeric_cols:
        if col not in df.columns:
            continue
        null_count = int(df[col].isnull().sum())
        if null_count == 0:
            continue
        if strategy == "mean":
            fill_val = df[col].mean()
        elif strategy == "zero":
            fill_val = 0.0
        else:  # median (default)
            fill_val = df[col].median()
        df[col] = df[col].fillna(fill_val)
        filled += null_count
    return filled


def _impute_text(
    df: pd.DataFrame,
    text_cols: List[str],
    strategy: str,
) -> int:
    """Fill or drop rows with missing text values.

    Returns the number of cells/rows handled.
    """
    handled = 0
    if strategy == "drop":
        before = len(df)
        df.dropna(subset=[c for c in text_cols if c in df.columns], inplace=True)
        handled = before - len(df)
    else:
        fill_val = str(strategy)
        for col in text_cols:
            if col not in df.columns:
                continue
            null_count = int(df[col].isnull().sum())
            if null_count:
                df[col] = df[col].fillna(fill_val)
                handled += null_count
    return handled


def _print_cleaning_summary(summary: Dict) -> None:
    """Print a human-readable cleaning summary."""
    separator = "=" * 65
    print(f"\n{separator}")
    print("  CLEANING SUMMARY")
    print(separator)
    print(f"  Rows before cleaning         : {summary['rows_before']}")
    print(f"  Exact duplicate rows removed : {summary['exact_dups_removed']}")
    print(f"  Duplicate ID rows removed    : {summary['id_dup_removed']}")
    if summary["id_conflicts"]:
        print(f"  ID conflicts detected        : {len(summary['id_conflicts'])}")
        for c in summary["id_conflicts"][:5]:
            cols = c["conflicting_cols"] or ["(no data conflicts — exact dup)"]
            print(f"    ID={c['id']}  ({c['count']} rows)  Conflict cols: {cols}")
    print(f"  Missing values before        : {summary['missing_before']}")
    if summary["invalid_values"]:
        print(f"  Out-of-range / non-numeric values replaced with NaN:")
        for col, cnt in summary["invalid_values"].items():
            print(f"    {col:<22}: {cnt} value(s)")
    print(f"  Text cells normalised        : {summary['text_fixes']}")
    print(
        f"  Numeric cells imputed "
        f"({summary['num_strategy']:<6})  : {summary['numeric_imputed']}"
    )
    print(
        f"  Text cells imputed "
        f"({summary['text_strategy']:<8})  : {summary['text_imputed']}"
    )
    print(f"  Missing values after         : {summary['missing_after']}")
    print(f"  Rows after cleaning          : {summary['rows_after']}")
    print(separator)

"""
pandas_analysis.py
==================
Pandas-based analysis for student and sales DataFrames:
  - Series creation, grade assignment, overview helpers
  - Filtering, sorting, groupby, pivot tables
  - Datetime conversion, monthly sales trends
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Grade configuration
# ---------------------------------------------------------------------------

GRADE_BINS = [0, 35, 45, 60, 75, 90, 101]
GRADE_LABELS = ["F", "D", "C", "B", "A", "A+"]
PASS_MARK = 35.0


# ---------------------------------------------------------------------------
# Series demo
# ---------------------------------------------------------------------------

def create_total_marks_series(df: pd.DataFrame) -> pd.Series:
    """Create a Pandas Series of total marks indexed by student name.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student DataFrame.

    Returns
    -------
    pd.Series
        Total marks (maths + science + english) with 'name' as index.
    """
    mark_cols = [c for c in ["maths", "science", "english"] if c in df.columns]
    if not mark_cols:
        return pd.Series(dtype=float, name="total_marks")
    totals = df[mark_cols].sum(axis=1)
    if "name" in df.columns:
        totals.index = df["name"].values
    totals.name = "total_marks"
    print("\n  Pandas Series — Total Marks by Student:")
    print(totals.to_string())
    return totals


# ---------------------------------------------------------------------------
# Grade assignment
# ---------------------------------------------------------------------------

def assign_grades(
    df: pd.DataFrame,
    pass_mark: float = PASS_MARK,
) -> pd.DataFrame:
    """Compute total, average, percentage, grade, and result columns.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student DataFrame.
    pass_mark : float
        Minimum mark per subject to pass.

    Returns
    -------
    pd.DataFrame
        New DataFrame (copy) with added columns.
    """
    df = df.copy()
    mark_cols = [c for c in ["maths", "science", "english"] if c in df.columns]
    if not mark_cols:
        return df

    max_per_subject = 100.0
    n_subjects = len(mark_cols)
    total_possible = max_per_subject * n_subjects

    df["total"] = df[mark_cols].sum(axis=1).round(2)
    df["average"] = df[mark_cols].mean(axis=1).round(2)
    df["percentage"] = (df["total"] / total_possible * 100).round(2)
    df["grade"] = pd.cut(
        df["percentage"],
        bins=GRADE_BINS,
        labels=GRADE_LABELS,
        right=False,
    )
    # Pass = ALL subjects >= pass_mark
    df["result"] = df[mark_cols].ge(pass_mark).all(axis=1).map(
        {True: "Pass", False: "Fail"}
    )
    return df


# ---------------------------------------------------------------------------
# Overview helpers
# ---------------------------------------------------------------------------

def print_overview(df: pd.DataFrame, label: str = "DataFrame") -> None:
    """Print info, describe, head, tail for the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Any DataFrame.
    label : str
        Label used in section header.
    """
    sep = "-" * 65
    print(f"\n{sep}")
    print(f"  OVERVIEW -- {label}")
    print(sep)
    print("\n  .info():")
    df.info()
    print("\n  .describe():")
    print(df.describe(include="all").to_string())
    print("\n  .head(5):")
    print(df.head(5).to_string())
    print("\n  .tail(5):")
    print(df.tail(5).to_string())
    print(sep)


def rename_reorder_drop(
    df: pd.DataFrame,
    rename_map: Optional[Dict[str, str]] = None,
    keep_cols: Optional[List[str]] = None,
    drop_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Utility to rename, reorder, or drop columns.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame (not mutated).
    rename_map : dict, optional
        {old_name: new_name}.
    keep_cols : list, optional
        Columns to keep (and their order). Columns not listed are dropped.
    drop_cols : list, optional
        Columns to remove.

    Returns
    -------
    pd.DataFrame
        Modified copy.
    """
    df = df.copy()
    if rename_map:
        df = df.rename(columns=rename_map)
    if drop_cols:
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    if keep_cols:
        df = df[[c for c in keep_cols if c in df.columns]]
    return df


def merge_students_departments(
    students_df: pd.DataFrame, dept_df: pd.DataFrame
) -> pd.DataFrame:
    """Merge student data with department info (left join).

    Parameters
    ----------
    students_df : pd.DataFrame
        Cleaned student DataFrame with 'department' column.
    dept_df : pd.DataFrame
        Departments lookup with 'department', 'HOD', 'building'.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame.
    """
    if dept_df is None or dept_df.empty:
        return students_df.copy()
    merged = students_df.merge(dept_df, on="department", how="left")
    print(f"\n  Merged students with departments: {merged.shape[0]} rows, "
          f"{merged.shape[1]} columns")
    return merged


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_students(
    df: pd.DataFrame,
    **conditions: Any,
) -> pd.DataFrame:
    """Filter student DataFrame by one or more column conditions.

    Supports:
    - Exact match  : dept="CSE"
    - Range        : attendance_pct_min=80.0, attendance_pct_max=100.0
    - isin list    : department_in=["CSE","ECE"]
    - OR logic     : Pass any additional kwarg pairs as _or_ combos using
                     the helper filter_or() separately.

    Parameters
    ----------
    df : pd.DataFrame
        Student or sales DataFrame.
    **conditions
        Keyword arguments encoding filters (see below).

    Naming conventions for kwargs
    ------------------------------
    ``col=value``          → exact equality
    ``col_min=value``      → col >= value
    ``col_max=value``      → col <= value
    ``col_in=[v1,v2,…]``   → col.isin([v1,v2,...])
    ``col_contains="text"``→ case-insensitive substring

    Returns
    -------
    pd.DataFrame
        Filtered copy.
    """
    mask = pd.Series([True] * len(df), index=df.index)

    for key, val in conditions.items():
        if key.endswith("_min"):
            col = key[:-4]
            if col in df.columns:
                mask &= df[col] >= val
        elif key.endswith("_max"):
            col = key[:-4]
            if col in df.columns:
                mask &= df[col] <= val
        elif key.endswith("_in"):
            col = key[:-3]
            if col in df.columns:
                mask &= df[col].isin(val if isinstance(val, list) else [val])
        elif key.endswith("_contains"):
            col = key[:-9]
            if col in df.columns:
                mask &= (
                    df[col]
                    .astype(str)
                    .str.contains(str(val), case=False, na=False)
                )
        else:
            if key in df.columns:
                mask &= df[key] == val

    result = df[mask].copy()
    if result.empty:
        print("  No matching records.")
    else:
        print(f"  Matching records: {len(result)}")
    return result


def filter_or(
    df: pd.DataFrame,
    conditions: List[Dict[str, Any]],
) -> pd.DataFrame:
    """Filter rows matching ANY of the given condition dicts (OR logic).

    Parameters
    ----------
    df : pd.DataFrame
    conditions : list of dict
        Each dict maps column → value.

    Returns
    -------
    pd.DataFrame
    """
    combined_mask = pd.Series([False] * len(df), index=df.index)
    for cond in conditions:
        m = pd.Series([True] * len(df), index=df.index)
        for col, val in cond.items():
            if col in df.columns:
                m &= df[col] == val
        combined_mask |= m
    return df[combined_mask].copy()


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def sort_data(
    df: pd.DataFrame,
    columns: Union[str, List[str]],
    ascending: Union[bool, List[bool]] = True,
    top_n: int = 0,
    add_rank: bool = False,
) -> pd.DataFrame:
    """Sort a DataFrame and optionally return only top / bottom N rows.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to sort.
    columns : str or list of str
        Column(s) to sort by.
    ascending : bool or list of bool
        Sort direction(s).
    top_n : int
        If > 0 return first top_n rows; if < 0 return last abs(top_n) rows.
    add_rank : bool
        If True, prepend a 'rank' column (1-based).

    Returns
    -------
    pd.DataFrame
        Sorted (and optionally sliced) copy.
    """
    if isinstance(columns, str):
        columns = [columns]
    if isinstance(ascending, bool):
        ascending = [ascending] * len(columns)
    df_sorted = df.sort_values(by=columns, ascending=ascending).copy()
    if top_n > 0:
        df_sorted = df_sorted.head(top_n)
    elif top_n < 0:
        df_sorted = df_sorted.tail(abs(top_n))
    if add_rank:
        df_sorted.insert(0, "rank", range(1, len(df_sorted) + 1))
    return df_sorted


# ---------------------------------------------------------------------------
# Groupby & aggregations
# ---------------------------------------------------------------------------

def group_summary(
    df: pd.DataFrame,
    by: Union[str, List[str]],
    aggregations: Dict[str, Union[str, List[str]]],
    label: str = "Group Summary",
) -> pd.DataFrame:
    """Group DataFrame and apply aggregations.

    Parameters
    ----------
    df : pd.DataFrame
    by : str or list of str
        Column(s) to group by.
    aggregations : dict
        Mapping of column → agg function(s), e.g.
        {"total": "sum", "average": ["mean", "max"]}.
    label : str
        Display label.

    Returns
    -------
    pd.DataFrame
        Aggregated result.
    """
    # Only keep agg columns that exist in df
    valid_agg = {
        col: funcs for col, funcs in aggregations.items() if col in df.columns
    }
    if not valid_agg:
        print(f"  [WARNING] No valid agg columns found for group_summary({label}).")
        return pd.DataFrame()
    result = df.groupby(by).agg(valid_agg)
    result.columns = [
        f"{col}_{fn}" if isinstance(fn, str) else f"{col}"
        for col, fn in (
            (c, f)
            for c, funcs in valid_agg.items()
            for f in (funcs if isinstance(funcs, list) else [funcs])
        )
    ]
    result = result.reset_index()
    print(f"\n  {label}:")
    print(result.to_string(index=False))
    return result


def grade_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return grade distribution counts and percentages.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a 'grade' column (from assign_grades()).

    Returns
    -------
    pd.DataFrame
        Distribution table.
    """
    if "grade" not in df.columns:
        return pd.DataFrame(columns=["grade", "count", "percentage"])
    vc = df["grade"].value_counts().reset_index()
    vc.columns = ["grade", "count"]
    vc["percentage"] = (vc["count"] / vc["count"].sum() * 100).round(2)
    return vc.sort_values("grade")


def value_counts_analysis(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Return value counts + percentages for a column.

    Parameters
    ----------
    df : pd.DataFrame
    col : str
        Column to analyse.

    Returns
    -------
    pd.DataFrame
        Table with value, count, percentage columns.
    """
    if col not in df.columns:
        return pd.DataFrame()
    vc = df[col].value_counts(dropna=False).reset_index()
    vc.columns = [col, "count"]
    vc["percentage"] = (vc["count"] / vc["count"].sum() * 100).round(2)
    return vc


def sales_pivot(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Create a pivot table of total revenue by region and category.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame with 'region', 'category', 'revenue' columns.

    Returns
    -------
    pd.DataFrame or None
    """
    needed = {"region", "category", "revenue"}
    if not needed.issubset(df.columns):
        return None
    pivot = pd.pivot_table(
        df,
        values="revenue",
        index="region",
        columns="category",
        aggfunc="sum",
        fill_value=0,
    )
    return pivot


def crosstab_region_category(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Return a cross-tabulation of region vs category.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame.

    Returns
    -------
    pd.DataFrame or None
    """
    if "region" not in df.columns or "category" not in df.columns:
        return None
    return pd.crosstab(df["region"], df["category"])


# ---------------------------------------------------------------------------
# Datetime & trends
# ---------------------------------------------------------------------------

def convert_order_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert order_date column to datetime and add year_month column.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame.

    Returns
    -------
    pd.DataFrame
        Modified copy with datetime order_date and year_month columns.
    """
    df = df.copy()
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["year_month"] = df["order_date"].dt.to_period("M")
    return df


def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Compute total revenue and order count per month.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame (should have been through convert_order_dates()).

    Returns
    -------
    pd.DataFrame
        Monthly summary with year_month, total_revenue, order_count.
    """
    if "year_month" not in df.columns:
        df = convert_order_dates(df)
    if "revenue" not in df.columns:
        if "quantity" in df.columns and "unit_price" in df.columns:
            df["revenue"] = df["quantity"] * df["unit_price"]
        else:
            return pd.DataFrame()

    monthly = (
        df.groupby("year_month")
        .agg(total_revenue=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
    )
    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    return monthly


def add_revenue_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add or recompute ``revenue = quantity * unit_price``.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame.

    Returns
    -------
    pd.DataFrame
        Copy with revenue column.
    """
    df = df.copy()
    if "quantity" in df.columns and "unit_price" in df.columns:
        df["revenue"] = (
            pd.to_numeric(df["quantity"], errors="coerce")
            * pd.to_numeric(df["unit_price"], errors="coerce")
        ).round(2)
    return df


def sales_group_analysis(df: pd.DataFrame) -> None:
    """Print region × category × product groupby analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Sales DataFrame with revenue column.
    """
    sep = "-" * 65
    if df.empty:
        print("  No data available for sales group analysis.")
        return

    # By region
    if {"region", "revenue", "order_id"}.issubset(df.columns):
        print(f"\n{sep}")
        print("  Sales by Region:")
        print(sep)
        region_grp = df.groupby("region").agg(
            total_revenue=("revenue", "sum"),
            avg_quantity=("quantity", "mean"),
            order_count=("order_id", "count"),
        ).round(2).reset_index()
        print(region_grp.to_string(index=False))

    # By category
    if {"category", "revenue"}.issubset(df.columns):
        print(f"\n{sep}")
        print("  Sales by Category:")
        print(sep)
        cat_grp = df.groupby("category").agg(
            total_revenue=("revenue", "sum"),
            avg_quantity=("quantity", "mean"),
            order_count=("order_id", "count"),
        ).round(2).reset_index()
        print(cat_grp.to_string(index=False))

    # By product
    if {"product", "revenue"}.issubset(df.columns):
        print(f"\n{sep}")
        print("  Sales by Product (Top 5):")
        print(sep)
        prod_grp = (
            df.groupby("product")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
        prod_grp.columns = ["product", "total_revenue"]
        print(prod_grp.to_string(index=False))

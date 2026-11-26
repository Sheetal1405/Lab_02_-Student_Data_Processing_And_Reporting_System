"""
numpy_analysis.py
=================
NumPy-based vectorised numerical analysis for student marks and sales data.
All computations use NumPy arrays, avoiding row-wise DataFrame loops.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Array construction & metadata
# ---------------------------------------------------------------------------

def extract_marks_array(
    df: pd.DataFrame,
    mark_cols: List[str] = None,
    verbose: bool = True,
) -> np.ndarray:
    """Convert marks columns from a DataFrame into a NumPy ndarray.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame with numeric columns.
    mark_cols : list of str, optional
        Column names to extract. Defaults to ["maths", "science", "english"].
    verbose : bool
        When True, print array metadata (shape, dtype, ndim, size).

    Returns
    -------
    np.ndarray
        2D array of shape (n_students, n_subjects).
    """
    if mark_cols is None:
        mark_cols = ["maths", "science", "english"]
    # Only use columns that exist
    mark_cols = [c for c in mark_cols if c in df.columns]
    if not mark_cols:
        raise ValueError("No valid mark columns found in DataFrame.")
    arr = df[mark_cols].to_numpy()
    if verbose:
        _print_array_metadata(arr, mark_cols)
    return arr


def _print_array_metadata(arr: np.ndarray, cols: List[str]) -> None:
    """Print array shape, dtype, ndim, and size."""
    separator = "-" * 55
    print(f"\n{separator}")
    print("  NumPy Array Metadata")
    print(separator)
    print(f"  Columns : {cols}")
    print(f"  Shape   : {arr.shape}")
    print(f"  Dtype   : {arr.dtype}")
    print(f"  Ndim    : {arr.ndim}")
    print(f"  Size    : {arr.size}")
    print(separator)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def numpy_statistics(arr: np.ndarray) -> Dict[str, float]:
    """Compute comprehensive statistics for a NumPy array.

    Parameters
    ----------
    arr : np.ndarray
        Numeric array (can be 1D or 2D).

    Returns
    -------
    dict
        Keys: mean, median, std, variance, min, max, q25, q50, q75.
    """
    # Flatten in case of 2D for overall statistics
    flat = arr.flatten()
    # Remove NaNs for robust computation
    clean = flat[~np.isnan(flat)]
    if clean.size == 0:
        # All NaNs → return 0
        return {k: 0.0 for k in [
            "mean", "median", "std", "variance", "min", "max",
            "q25", "q50", "q75",
        ]}
    return {
        "mean":     float(np.mean(clean)),
        "median":   float(np.median(clean)),
        "std":      float(np.std(clean, ddof=1)) if clean.size > 1 else 0.0,
        "variance": float(np.var(clean, ddof=1)) if clean.size > 1 else 0.0,
        "min":      float(np.min(clean)),
        "max":      float(np.max(clean)),
        "q25":      float(np.percentile(clean, 25)),
        "q50":      float(np.percentile(clean, 50)),
        "q75":      float(np.percentile(clean, 75)),
    }


def row_wise_ops(arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute total and average marks per student (row).

    Parameters
    ----------
    arr : np.ndarray
        2D array of shape (n_students, n_subjects).

    Returns
    -------
    (totals, averages) : (np.ndarray, np.ndarray)
        1D arrays of length n_students.
    """
    _validate_2d(arr, "row_wise_ops")
    # Use nansum/nanmean to handle NaN gracefully
    totals = np.nansum(arr, axis=1)
    averages = np.nanmean(arr, axis=1)
    return totals, averages


def column_wise_ops(
    arr: np.ndarray, mark_cols: List[str]
) -> Dict[str, Dict[str, float]]:
    """Compute subject-wise (column-wise) statistics.

    Parameters
    ----------
    arr : np.ndarray
        2D array of shape (n_students, n_subjects).
    mark_cols : list of str
        Subject names (must match arr columns).

    Returns
    -------
    dict
        Mapping of subject → {mean, median, std, min, max}.
    """
    _validate_2d(arr, "column_wise_ops")
    if arr.shape[1] != len(mark_cols):
        raise ValueError(
            f"Array has {arr.shape[1]} columns but {len(mark_cols)} "
            "names were provided."
        )
    stats = {}
    for idx, col in enumerate(mark_cols):
        col_data = arr[:, idx]
        clean = col_data[~np.isnan(col_data)]
        if clean.size == 0:
            stats[col] = {
                "mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0,
            }
        else:
            stats[col] = {
                "mean":   float(np.mean(clean)),
                "median": float(np.median(clean)),
                "std":    float(np.std(clean, ddof=1)) if clean.size > 1 else 0.0,
                "min":    float(np.min(clean)),
                "max":    float(np.max(clean)),
            }
    return stats


# ---------------------------------------------------------------------------
# Boolean masking, clipping, and conditional operations
# ---------------------------------------------------------------------------

def find_failing_scores(
    arr: np.ndarray,
    pass_mark: float = 35.0,
) -> Tuple[np.ndarray, int]:
    """Use boolean masking to find marks below the pass threshold.

    Parameters
    ----------
    arr : np.ndarray
        Marks array.
    pass_mark : float
        Minimum passing mark.

    Returns
    -------
    (failing_mask, count)
        Boolean mask of same shape, and total count of failing cells.
    """
    failing = arr < pass_mark
    return failing, int(np.sum(failing))


def apply_grace_marks(
    arr: np.ndarray,
    grace: float = 5.0,
    cap: float = 100.0,
) -> np.ndarray:
    """Add grace marks to all entries, capping at max allowed.

    Parameters
    ----------
    arr : np.ndarray
        Source array (not mutated).
    grace : float
        Marks to add.
    cap : float
        Maximum allowed mark after grace.

    Returns
    -------
    np.ndarray
        New array with grace applied and clipped.
    """
    curved = arr + grace
    return np.clip(curved, a_min=None, a_max=cap)


def pass_fail_labels(
    totals: np.ndarray,
    threshold: float = 105.0,  # 35×3=105 for 3 subjects
) -> np.ndarray:
    """Return 'Pass'/'Fail' labels using np.where().

    Parameters
    ----------
    totals : np.ndarray
        1D array of total marks per student.
    threshold : float
        Minimum total to pass.

    Returns
    -------
    np.ndarray of dtype object (strings 'Pass' or 'Fail').
    """
    return np.where(totals >= threshold, "Pass", "Fail")


def rank_students(totals: np.ndarray, ascending: bool = False) -> np.ndarray:
    """Return rank indices using np.argsort().

    Parameters
    ----------
    totals : np.ndarray
        1D array of scores.
    ascending : bool
        When False (default), highest score gets rank 0.

    Returns
    -------
    np.ndarray of int
        Indices that would sort the array in the specified order.
    """
    if ascending:
        return np.argsort(totals)
    else:
        return np.argsort(totals)[::-1]


# ---------------------------------------------------------------------------
# Demonstration / Reporting
# ---------------------------------------------------------------------------

def print_numpy_analysis_demo(
    df: pd.DataFrame,
    mark_cols: List[str] = None,
) -> None:
    """Comprehensive NumPy analysis demonstration for student marks.

    Parameters
    ----------
    df : pd.DataFrame
        Student DataFrame.
    mark_cols : list of str, optional
        Columns to treat as marks. Defaults to ["maths", "science", "english"].
    """
    separator = "=" * 65

    print(f"\n{separator}")
    print("  NUMPY NUMERICAL ANALYSIS DEMO")
    print(separator)

    if mark_cols is None:
        mark_cols = ["maths", "science", "english"]
    mark_cols = [c for c in mark_cols if c in df.columns]

    # -- Step 1: convert to ndarray -------------------------------------------
    arr = extract_marks_array(df, mark_cols, verbose=True)

    # -- Step 2: overall statistics -------------------------------------------
    overall = numpy_statistics(arr)
    print("\n  Overall Statistics (all marks combined):")
    print(f"    Mean      : {overall['mean']:>8.2f}")
    print(f"    Median    : {overall['median']:>8.2f}")
    print(f"    Std       : {overall['std']:>8.2f}")
    print(f"    Variance  : {overall['variance']:>8.2f}")
    print(f"    Min       : {overall['min']:>8.2f}")
    print(f"    Max       : {overall['max']:>8.2f}")
    print(f"    25th %ile : {overall['q25']:>8.2f}")
    print(f"    50th %ile : {overall['q50']:>8.2f}")
    print(f"    75th %ile : {overall['q75']:>8.2f}")

    # -- Step 3: row-wise operations ------------------------------------------
    totals, averages = row_wise_ops(arr)
    print("\n  Row-wise Operations (per student):")
    print(f"    Total marks (sum)   : shape={totals.shape}, sample={totals[:3]}")
    print(f"    Average marks       : shape={averages.shape}, sample={averages[:3]}")

    # -- Step 4: column-wise operations ---------------------------------------
    col_stats = column_wise_ops(arr, mark_cols)
    print("\n  Column-wise (Subject) Statistics:")
    for subj, stats_dict in col_stats.items():
        print(f"    {subj.upper():<10} → "
              f"Mean={stats_dict['mean']:>6.2f}, "
              f"Median={stats_dict['median']:>6.2f}, "
              f"Std={stats_dict['std']:>6.2f}, "
              f"Min={stats_dict['min']:>6.2f}, "
              f"Max={stats_dict['max']:>6.2f}")

    # -- Step 5: boolean masking (failing scores) -----------------------------
    failing_mask, fail_count = find_failing_scores(arr, pass_mark=35.0)
    print(f"\n  Boolean Masking (marks < 35):")
    print(f"    Failing cells count : {fail_count}")
    if fail_count > 0 and fail_count <= 10:
        print(f"    Mask sample:\n{failing_mask[:3]}")

    # -- Step 6: apply grace marks (clipping) ---------------------------------
    grace_arr = apply_grace_marks(arr, grace=5.0, cap=100.0)
    print(f"\n  Grace Marks (+5, capped at 100):")
    print(f"    Original sample : {arr[0]}")
    print(f"    After grace     : {grace_arr[0]}")

    # -- Step 7: pass/fail labels via np.where() ------------------------------
    # Assume pass = total >= 105 (3 subjects × 35)
    labels = pass_fail_labels(totals, threshold=105.0)
    pass_count = int(np.sum(labels == "Pass"))
    fail_count_label = int(np.sum(labels == "Fail"))
    print(f"\n  Pass/Fail Classification (threshold = 105 total):")
    print(f"    Pass count : {pass_count}")
    print(f"    Fail count : {fail_count_label}")
    print(f"    Sample labels : {labels[:5]}")

    # -- Step 8: ranking via np.argsort() -------------------------------------
    ranked_indices = rank_students(totals, ascending=False)
    print(f"\n  Student Ranking by Total Marks (descending):")
    print(f"    Top 5 indices : {ranked_indices[:5]}")
    print(f"    Top 5 totals  : {totals[ranked_indices[:5]]}")

    print(f"\n{separator}\n")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_2d(arr: np.ndarray, func_name: str) -> None:
    """Ensure *arr* is 2D or raise ValueError."""
    if arr.ndim != 2:
        raise ValueError(
            f"{func_name} requires a 2D array; got ndim={arr.ndim}."
        )

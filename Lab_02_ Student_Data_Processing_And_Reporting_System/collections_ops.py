"""
collections_ops.py
==================
Demonstrates Python built-in collection operations on student records:
lists, dicts, tuples, sets, sorting, and frequency analysis.
"""

from typing import Any, Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# Constants stored as tuples (immutable, hashable)
# ---------------------------------------------------------------------------

#: Subject names used throughout the system
SUBJECTS: Tuple[str, ...] = ("maths", "science", "english")

#: Grade boundaries: (min_pct, max_pct, grade_label)
GRADE_BOUNDARIES: Tuple[Tuple[float, float, str], ...] = (
    (90.0, 100.0, "A+"),
    (75.0,  89.9, "A"),
    (60.0,  74.9, "B"),
    (45.0,  59.9, "C"),
    (35.0,  44.9, "D"),
    (0.0,   34.9, "F"),
)

#: Thresholds used in various analyses
THRESHOLDS: Tuple[Tuple[str, float], ...] = (
    ("pass_mark", 35.0),
    ("low_attendance", 75.0),
    ("max_mark", 100.0),
    ("min_mark", 0.0),
)

#: Helper constant for pass mark lookup
PASS_MARK: float = dict(THRESHOLDS)["pass_mark"]
LOW_ATTENDANCE: float = dict(THRESHOLDS)["low_attendance"]


# ---------------------------------------------------------------------------
# Core collection functions
# ---------------------------------------------------------------------------

def unique_values(records: List[Dict], key: str) -> Set[Any]:
    """Return the unique values for *key* across all records.

    Parameters
    ----------
    records : list of dict
        Student records.
    key : str
        Dictionary key to extract.

    Returns
    -------
    set
        Unique values found (empty set if key is absent in all records).
    """
    return {rec[key] for rec in records if key in rec}


def count_frequency(items: List[Any]) -> Dict[Any, int]:
    """Return a frequency count dictionary for the given list of items.

    Parameters
    ----------
    items : list
        Any flat list of hashable values.

    Returns
    -------
    dict
        Mapping of value → count, sorted by count descending.
    """
    freq: Dict[Any, int] = {}
    for item in items:
        freq[item] = freq.get(item, 0) + 1
    return dict(sorted(freq.items(), key=lambda kv: kv[1], reverse=True))


def set_operations(
    records: List[Dict],
    dept_filter: str = "CSE",
    attendance_threshold: float = LOW_ATTENDANCE,
) -> Dict[str, Set[str]]:
    """Perform set operations comparing two student groups.

    Groups compared:
    - *dept_set*: student names in ``dept_filter`` department.
    - *attendance_set*: student names with attendance > ``attendance_threshold``.

    Parameters
    ----------
    records : list of dict
        Student records with at least 'name', 'department', 'attendance_pct'.
    dept_filter : str
        Department code to use for the first set.
    attendance_threshold : float
        Minimum attendance percentage for the second set.

    Returns
    -------
    dict with keys:
        'dept_set', 'attendance_set', 'union', 'intersection', 'dept_only',
        'attendance_only'
    """
    dept_set: Set[str] = {
        rec["name"]
        for rec in records
        if str(rec.get("department", "")).strip().upper() == dept_filter.upper()
    }
    attendance_set: Set[str] = {
        rec["name"]
        for rec in records
        if _safe_float(rec.get("attendance_pct")) > attendance_threshold
    }

    return {
        "dept_set": dept_set,
        "attendance_set": attendance_set,
        "union": dept_set | attendance_set,
        "intersection": dept_set & attendance_set,
        "dept_only": dept_set - attendance_set,
        "attendance_only": attendance_set - dept_set,
    }


def sort_by_key(
    records: List[Dict],
    sort_key: str,
    ascending: bool = False,
    top_n: int = 0,
) -> List[Dict]:
    """Sort a list of dicts by a numeric or string key.

    Parameters
    ----------
    records : list of dict
        Records to sort.
    sort_key : str
        Key to sort by.
    ascending : bool
        Sort order. Default is descending (False).
    top_n : int
        If > 0, return only the first *top_n* results after sorting.

    Returns
    -------
    list of dict
        Sorted (and optionally sliced) records.
    """
    def _sort_val(rec: Dict) -> Any:
        val = rec.get(sort_key)
        if val is None:
            # Put None values at the end
            return float("-inf") if not ascending else float("inf")
        return val

    sorted_records = sorted(records, key=_sort_val, reverse=not ascending)
    return sorted_records[:top_n] if top_n > 0 else sorted_records


def records_from_dataframe(df: "pd.DataFrame") -> List[Dict]:  # type: ignore[name-defined]
    """Convert a Pandas DataFrame to a list of dicts.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.

    Returns
    -------
    list of dict
        Each row as an independent dictionary.
    """
    return df.to_dict(orient="records")


def compute_total_marks(record: Dict) -> float:
    """Return the sum of marks across all subjects for one student record.

    Parameters
    ----------
    record : dict
        A single student record.

    Returns
    -------
    float
        Sum of maths + science + english (treating missing as 0).
    """
    return sum(_safe_float(record.get(subj, 0)) for subj in SUBJECTS)


def enrich_records(records: List[Dict]) -> List[Dict]:
    """Add ``total_marks`` and ``average_marks`` fields to each record.

    Parameters
    ----------
    records : list of dict
        Student records.

    Returns
    -------
    list of dict
        New list with enriched records (originals not mutated).
    """
    enriched = []
    for rec in records:
        new_rec = dict(rec)
        total = compute_total_marks(new_rec)
        n_subjects = len(SUBJECTS)
        new_rec["total_marks"] = round(total, 2)
        new_rec["average_marks"] = round(total / n_subjects, 2) if n_subjects else 0.0
        enriched.append(new_rec)
    return enriched


def print_collections_demo(records: List[Dict]) -> None:
    """Print a formatted demonstration of all collection operations.

    Parameters
    ----------
    records : list of dict
        Student records to process.
    """
    separator = "=" * 65

    print(f"\n{separator}")
    print("  PYTHON COLLECTIONS OPERATIONS DEMO")
    print(separator)

    # Unique departments
    depts = unique_values(records, "department")
    print(f"\n  Unique Departments : {sorted(depts)}")

    # Unique cities
    cities = unique_values(records, "city")
    print(f"  Unique Cities      : {sorted(cities)}")

    # Department frequency
    dept_freq = count_frequency([rec.get("department", "N/A") for rec in records])
    print("\n  Department Frequency:")
    for dept, cnt in dept_freq.items():
        print(f"    {dept:<10} → {cnt} student(s)")

    # City frequency
    city_freq = count_frequency([rec.get("city", "N/A") for rec in records])
    print("\n  City Frequency:")
    for city, cnt in list(city_freq.items())[:6]:
        print(f"    {city:<12} → {cnt} student(s)")

    # Set operations
    ops = set_operations(records, dept_filter="CSE", attendance_threshold=75.0)
    print("\n  Set Operations (CSE dept  vs  Attendance > 75%):")
    print(f"    CSE students         : {sorted(ops['dept_set'])}")
    print(f"    Good attendance      : {sorted(ops['attendance_set'])}")
    print(f"    Union                : {len(ops['union'])} students")
    print(f"    Intersection         : {sorted(ops['intersection'])}")
    print(f"    CSE only (low attend): {sorted(ops['dept_only'])}")
    print(f"    Good attend, not CSE : {sorted(ops['attendance_only'])}")

    # Sort by total marks (top 5)
    enriched = enrich_records(records)
    top5 = sort_by_key(enriched, "total_marks", ascending=False, top_n=5)
    print("\n  Top 5 Students by Total Marks:")
    print(f"    {'Name':<20} {'Dept':<8} {'Total':>8} {'Avg':>8}")
    print(f"    {'-'*20} {'-'*8} {'-'*8} {'-'*8}")
    for r in top5:
        print(
            f"    {str(r.get('name','?')):<20} "
            f"{str(r.get('department','?')):<8} "
            f"{r.get('total_marks', 0):>8.2f} "
            f"{r.get('average_marks', 0):>8.2f}"
        )

    print(f"\n{separator}\n")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _safe_float(value: Any) -> float:
    """Safely cast *value* to float; return 0.0 on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

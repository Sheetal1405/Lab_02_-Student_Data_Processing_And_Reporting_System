"""
main.py
=======
Student and Business Data Processing & Analytical Reporting System
==================================================================
Entry point.  Run from the project root:
    python main.py

The menu drives the full data pipeline through two parallel tracks:
  Track A — Student data processing, collections ops, NumPy, Pandas, reports
  Track B — Sales data processing, Pandas analysis, pivot tables, reports
"""

import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Allow running from any working directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


# ---------------------------------------------------------------------------
# Local module imports
# ---------------------------------------------------------------------------
import data_loader as dl
import data_cleaning as dc
import collections_ops as co
import numpy_analysis as na
import pandas_analysis as pa
import reports as rp


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

MENU = """
╔══════════════════════════════════════════════════════════════════════╗
║  Student and Business Data Processing & Analytical Reporting System  ║
╚══════════════════════════════════════════════════════════════════════╝

  STUDENT PIPELINE
  ─────────────────────────────────────────────────────────────────────
  [1]  Load clean student data
  [2]  Load DIRTY student data (demonstrates full cleaning pipeline)
  [3]  Python collections demo (sets, dicts, sorting)
  [4]  NumPy numerical analysis demo
  [5]  Pandas analysis demo (grades, filtering, groupby, pivot tables)
  [6]  Generate student performance report + export
  [7]  Generate data quality report (uses last loaded data)

  SALES PIPELINE
  ─────────────────────────────────────────────────────────────────────
  [8]  Load clean sales data
  [9]  Load DIRTY sales data (demonstrates full cleaning pipeline)
  [10] Pandas sales analysis (groupby, pivot, crosstab, monthly trend)
  [11] Generate sales analytical report + export

  COMBINED / SYSTEM
  ─────────────────────────────────────────────────────────────────────
  [12] Run FULL PIPELINE (all steps in sequence, clean data)
  [13] Run FULL PIPELINE (all steps, dirty data)

  [0]  Exit

  Enter choice: """


# ---------------------------------------------------------------------------
# Global state (shared across menu choices)
# ---------------------------------------------------------------------------
_state = {
    "students_df":       None,  # clean loaded DataFrame
    "students_clean_df": None,  # after cleaning
    "students_graded_df": None, # after assign_grades
    "clean_summary":     None,  # dict from data_cleaning.clean_data()
    "sales_df":          None,
    "sales_clean_df":    None,
    "dept_df":           None,
}


# ---------------------------------------------------------------------------
# Individual pipeline steps
# ---------------------------------------------------------------------------

def step_load_students(dirty: bool = False) -> None:
    """Load student CSV into state."""
    fname = "students_dirty.csv" if dirty else "students.csv"
    path = DATA_DIR / fname
    df = dl.load_csv(str(path), required_cols=dl.STUDENT_REQUIRED_COLS)
    if df is not None:
        _state["students_df"] = df
        label = "dirty" if dirty else "clean"
        print(f"\n  ✓ Student dataset ({label}) loaded: {df.shape}")
    else:
        print(f"  ✗ Failed to load {fname}.")


def step_clean_students() -> None:
    """Clean student data and store result + summary."""
    if _state["students_df"] is None:
        print("  No student data loaded. Run option 1 or 2 first.")
        return
    # Show missing report before cleaning
    dc.missing_report(_state["students_df"], label="Students (before cleaning)")
    clean_df, summary = dc.clean_data(
        _state["students_df"],
        dataset_type="student",
        num_strategy="median",
        text_strategy="Unknown",
    )
    _state["students_clean_df"] = clean_df
    _state["clean_summary"] = summary
    print(f"\n  ✓ Student data cleaned: {clean_df.shape}")


def step_collections() -> None:
    """Run collections operations demo."""
    source = _state["students_clean_df"] or _state["students_df"]
    if source is None:
        print("  Load student data first (options 1 or 2).")
        return
    records = co.records_from_dataframe(source)
    co.print_collections_demo(records)


def step_numpy() -> None:
    """Run NumPy analysis demo."""
    source = _state["students_clean_df"] or _state["students_df"]
    if source is None:
        print("  Load student data first (options 1 or 2).")
        return
    na.print_numpy_analysis_demo(source)


def step_pandas_students() -> None:
    """Run full Pandas analysis on student data."""
    source = _state["students_clean_df"] or _state["students_df"]
    if source is None:
        print("  Load student data first (options 1 or 2).")
        return

    sep = "═" * 65
    print(f"\n{sep}")
    print("  PANDAS ANALYSIS — STUDENT DATA")
    print(sep)

    # Create total marks Series
    pa.create_total_marks_series(source)

    # Assign grades
    graded = pa.assign_grades(source)
    _state["students_graded_df"] = graded
    print("\n  After grade assignment (first 5 rows):")
    print(graded[["name", "total", "average", "percentage", "grade", "result"]].head().to_string(index=False))

    # Merge with departments
    if _state["dept_df"] is None:
        dept_path = DATA_DIR / "departments.csv"
        _state["dept_df"] = dl.load_csv(str(dept_path), verbose=False)
    if _state["dept_df"] is not None:
        merged = pa.merge_students_departments(graded, _state["dept_df"])
        print("\n  Merged with department info (first 3 rows):")
        print(merged.head(3).to_string(index=False))

    # Filtering demo
    print("\n  Filter: CSE students with average > 80")
    pa.filter_students(graded, department="Cse", average_min=80)

    print("\n  Filter: students with attendance_pct < 75 (attendance concerns)")
    pa.filter_students(graded, attendance_pct_max=74.9)

    print("\n  Filter: students in CSE or ECE (isin demo)")
    pa.filter_students(graded, department_in=["Cse", "Ece"])

    # Sorting
    print("\n  Sort: Top 5 by total marks (descending):")
    top5 = pa.sort_data(graded, columns="total", ascending=False, top_n=5, add_rank=True)
    print(top5[["rank", "name", "department", "total", "grade"]].to_string(index=False))

    print("\n  Sort: Bottom 5 by total marks (ascending):")
    bot5 = pa.sort_data(graded, columns="total", ascending=True, top_n=5, add_rank=True)
    print(bot5[["rank", "name", "department", "total", "grade"]].to_string(index=False))

    # Groupby summary
    pa.group_summary(
        graded, by="department",
        aggregations={
            "total": ["mean", "max"],
            "attendance_pct": "mean",
        },
        label="Department-wise Marks Summary",
    )

    # Grade distribution
    grade_dist = pa.grade_distribution(graded)
    print("\n  Grade Distribution:")
    print(grade_dist.to_string(index=False))

    # Value counts
    gender_vc = pa.value_counts_analysis(graded, "gender")
    print("\n  Gender Distribution:")
    print(gender_vc.to_string(index=False))

    print(f"\n{sep}\n")


def step_student_report() -> None:
    """Generate and optionally export student report."""
    source = _state["students_graded_df"] or _state["students_clean_df"] or _state["students_df"]
    if source is None:
        print("  Load student data first (options 1 or 2).")
        return
    # Ensure grades are assigned
    if "grade" not in source.columns:
        source = pa.assign_grades(source)
        _state["students_graded_df"] = source

    answer = input("\n  Export reports to output/? (y/n): ").strip().lower()
    export = answer == "y"
    rp.student_report(
        source,
        attendance_threshold=75.0,
        export_csv=export,
        export_txt=export,
        output_dir=str(OUTPUT_DIR),
    )


def step_dq_report() -> None:
    """Generate data quality report from last cleaning summary."""
    if _state["clean_summary"] is None:
        print("  No cleaning summary available. Load dirty data first (option 2).")
        return
    answer = input("\n  Export report to output/? (y/n): ").strip().lower()
    export = answer == "y"
    rp.data_quality_report(
        _state["clean_summary"],
        export_txt=export,
        output_dir=str(OUTPUT_DIR),
    )


def step_load_sales(dirty: bool = False) -> None:
    """Load sales CSV into state."""
    fname = "sales_dirty.csv" if dirty else "sales.csv"
    path = DATA_DIR / fname
    df = dl.load_csv(str(path), required_cols=dl.SALES_REQUIRED_COLS)
    if df is not None:
        _state["sales_df"] = df
        label = "dirty" if dirty else "clean"
        print(f"\n  ✓ Sales dataset ({label}) loaded: {df.shape}")
    else:
        print(f"  ✗ Failed to load {fname}.")


def step_clean_sales() -> None:
    """Clean sales data."""
    if _state["sales_df"] is None:
        print("  No sales data loaded. Run option 8 or 9 first.")
        return
    dc.missing_report(_state["sales_df"], label="Sales (before cleaning)")
    clean_df, summary = dc.clean_data(
        _state["sales_df"],
        dataset_type="sales",
        num_strategy="median",
        text_strategy="Unknown",
    )
    # Add revenue column
    clean_df = pa.add_revenue_column(clean_df)
    _state["sales_clean_df"] = clean_df
    # Only overwrite clean_summary if no student summary exists
    if _state["clean_summary"] is None:
        _state["clean_summary"] = summary
    print(f"\n  ✓ Sales data cleaned: {clean_df.shape}")


def step_pandas_sales() -> None:
    """Run full Pandas sales analysis."""
    source = _state["sales_clean_df"] or _state["sales_df"]
    if source is None:
        print("  Load sales data first (options 8 or 9).")
        return
    # Ensure revenue
    if "revenue" not in source.columns:
        source = pa.add_revenue_column(source)
        _state["sales_clean_df"] = source

    sep = "═" * 65
    print(f"\n{sep}")
    print("  PANDAS ANALYSIS — SALES DATA")
    print(sep)

    pa.sales_group_analysis(source)

    # Pivot table
    pivot = pa.sales_pivot(source)
    if pivot is not None:
        print("\n  Pivot Table — Revenue by Region × Category:")
        print(pivot.to_string())

    # Crosstab
    ct = pa.crosstab_region_category(source)
    if ct is not None:
        print("\n  Cross-tabulation — Region × Category (order counts):")
        print(ct.to_string())

    # Category value counts
    cat_vc = pa.value_counts_analysis(source, "category")
    print("\n  Category Value Counts:")
    print(cat_vc.to_string(index=False))

    # Monthly trend
    monthly = pa.monthly_sales_trend(source)
    if not monthly.empty:
        print("\n  Monthly Sales Trend:")
        print(monthly.to_string(index=False))

    # Filtering demo
    print("\n  Filter: Electronics in North region")
    pa.filter_students(source, category="Electronics", region="North")

    print("\n  Filter: revenue > 50000")
    pa.filter_students(source, revenue_min=50000)

    print(f"\n{sep}\n")


def step_sales_report() -> None:
    """Generate and optionally export sales report."""
    source = _state["sales_clean_df"] or _state["sales_df"]
    if source is None:
        print("  Load sales data first (options 8 or 9).")
        return
    if "revenue" not in source.columns:
        source = pa.add_revenue_column(source)

    answer = input("\n  Export reports to output/? (y/n): ").strip().lower()
    export = answer == "y"
    rp.sales_report(
        source,
        export_csv=export,
        export_txt=export,
        output_dir=str(OUTPUT_DIR),
    )


def _full_pipeline(dirty: bool = False) -> None:
    """Execute the entire pipeline in sequence."""
    label = "DIRTY" if dirty else "CLEAN"
    banner = f" FULL PIPELINE — {label} DATA "
    sep = "▶" * 70
    print(f"\n{sep}")
    print(banner.center(70))
    print(sep)

    # Student track
    step_load_students(dirty=dirty)
    step_clean_students()
    step_collections()
    step_numpy()
    step_pandas_students()
    step_student_report_no_prompt(export=False)
    step_dq_report_no_prompt(export=False)

    # Sales track
    step_load_sales(dirty=dirty)
    step_clean_sales()
    step_pandas_sales()
    step_sales_report_no_prompt(export=False)

    print(f"\n{sep}")
    print("  FULL PIPELINE COMPLETE".center(70))
    print(sep)


def step_student_report_no_prompt(export: bool) -> None:
    source = _state["students_graded_df"] or _state["students_clean_df"] or _state["students_df"]
    if source is None:
        return
    if "grade" not in source.columns:
        source = pa.assign_grades(source)
        _state["students_graded_df"] = source
    rp.student_report(source, export_csv=export, export_txt=export, output_dir=str(OUTPUT_DIR))


def step_dq_report_no_prompt(export: bool) -> None:
    if _state["clean_summary"] is None:
        return
    rp.data_quality_report(_state["clean_summary"], export_txt=export, output_dir=str(OUTPUT_DIR))


def step_sales_report_no_prompt(export: bool) -> None:
    source = _state["sales_clean_df"] or _state["sales_df"]
    if source is None:
        return
    if "revenue" not in source.columns:
        source = pa.add_revenue_column(source)
    rp.sales_report(source, export_csv=export, export_txt=export, output_dir=str(OUTPUT_DIR))


# ---------------------------------------------------------------------------
# Menu dispatcher
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point — present interactive CLI menu."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        choice = input(MENU).strip()

        if choice == "0":
            print("\n  Goodbye.\n")
            break
        elif choice == "1":
            step_load_students(dirty=False)
        elif choice == "2":
            step_load_students(dirty=True)
            step_clean_students()
        elif choice == "3":
            step_collections()
        elif choice == "4":
            step_numpy()
        elif choice == "5":
            step_pandas_students()
        elif choice == "6":
            step_student_report()
        elif choice == "7":
            step_dq_report()
        elif choice == "8":
            step_load_sales(dirty=False)
        elif choice == "9":
            step_load_sales(dirty=True)
            step_clean_sales()
        elif choice == "10":
            step_pandas_sales()
        elif choice == "11":
            step_sales_report()
        elif choice == "12":
            _full_pipeline(dirty=False)
        elif choice == "13":
            _full_pipeline(dirty=True)
        else:
            print("  Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main()

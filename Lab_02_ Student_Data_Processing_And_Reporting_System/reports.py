"""
reports.py
==========
Generate formatted analytical reports for student, sales, and data quality.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


# ---------------------------------------------------------------------------
# Student Report
# ---------------------------------------------------------------------------

def student_report(
    df: pd.DataFrame,
    attendance_threshold: float = 75.0,
    export_csv: bool = False,
    export_txt: bool = False,
    output_dir: str = "output",
) -> str:
    """Generate a comprehensive student performance report.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student DataFrame (expected to have 'total', 'average',
        'percentage', 'grade', 'result').
    attendance_threshold : float
        Minimum acceptable attendance percentage.
    export_csv : bool
        If True, save summary tables to CSV in output_dir.
    export_txt : bool
        If True, save the full text report to .txt in output_dir.
    output_dir : str
        Directory for exports.

    Returns
    -------
    str
        The full report text.
    """
    if df.empty:
        return "[STUDENT REPORT]\nNo data available."

    sep_main = "═" * 70
    sep_sub = "─" * 70

    report_lines = []
    report_lines.append(sep_main)
    report_lines.append("           STUDENT PERFORMANCE ANALYTICAL REPORT")
    report_lines.append(sep_main)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(sep_sub)
    report_lines.append("")

    # === SECTION 1: Overall Statistics =====================================
    report_lines.append("1. OVERALL STATISTICS")
    report_lines.append(sep_sub)
    report_lines.append(f"  Total Students       : {len(df)}")
    if "result" in df.columns:
        pass_count = int((df["result"] == "Pass").sum())
        fail_count = int((df["result"] == "Fail").sum())
        pass_rate = (pass_count / len(df) * 100) if len(df) > 0 else 0.0
        report_lines.append(f"  Passed               : {pass_count} ({pass_rate:.2f}%)")
        report_lines.append(f"  Failed               : {fail_count}")
    if "average" in df.columns:
        avg_overall = df["average"].mean()
        report_lines.append(f"  Average Score        : {avg_overall:.2f}")
    if "attendance_pct" in df.columns:
        avg_att = df["attendance_pct"].mean()
        report_lines.append(f"  Average Attendance   : {avg_att:.2f}%")
    report_lines.append("")

    # === SECTION 2: Department Summary =====================================
    report_lines.append("2. DEPARTMENT-WISE SUMMARY")
    report_lines.append(sep_sub)
    if "department" in df.columns:
        dept_summary = (
            df.groupby("department")
            .agg(
                count=("student_id", "count"),
                avg_score=("average", "mean"),
                pass_count=("result", lambda x: (x == "Pass").sum()),
            )
            .round(2)
            .reset_index()
        )
        dept_summary.columns = ["Department", "Students", "Avg Score", "Pass Count"]
        report_lines.append(dept_summary.to_string(index=False))
        if export_csv:
            _export_table(dept_summary, "department_summary.csv", output_dir)
    else:
        report_lines.append("  Department data not available.")
    report_lines.append("")

    # === SECTION 3: Top 5 and Bottom 5 ====================================
    report_lines.append("3. PERFORMANCE RANKING")
    report_lines.append(sep_sub)
    if "total" in df.columns:
        top_5 = df.nlargest(5, "total")[[
            "name", "department", "total", "average", "grade"
        ]]
        report_lines.append("  Top 5 Students:")
        report_lines.append(top_5.to_string(index=False))
        report_lines.append("")
        bottom_5 = df.nsmallest(5, "total")[[
            "name", "department", "total", "average", "grade"
        ]]
        report_lines.append("  Bottom 5 Students:")
        report_lines.append(bottom_5.to_string(index=False))
        if export_csv:
            _export_table(top_5, "top_students.csv", output_dir)
            _export_table(bottom_5, "bottom_students.csv", output_dir)
    else:
        report_lines.append("  Total marks not computed.")
    report_lines.append("")

    # === SECTION 4: Grade Distribution =====================================
    report_lines.append("4. GRADE DISTRIBUTION")
    report_lines.append(sep_sub)
    if "grade" in df.columns:
        grade_dist = (
            df["grade"]
            .value_counts(dropna=False)
            .reset_index()
        )
        grade_dist.columns = ["Grade", "Count"]
        grade_dist["Percentage"] = (
            grade_dist["Count"] / grade_dist["Count"].sum() * 100
        ).round(2)
        grade_dist = grade_dist.sort_values("Grade")
        report_lines.append(grade_dist.to_string(index=False))
        if export_csv:
            _export_table(grade_dist, "grade_distribution.csv", output_dir)
    else:
        report_lines.append("  Grade data not available.")
    report_lines.append("")

    # === SECTION 5: Attendance Concerns ====================================
    report_lines.append("5. ATTENDANCE CONCERNS")
    report_lines.append(sep_sub)
    if "attendance_pct" in df.columns:
        low_att = df[df["attendance_pct"] < attendance_threshold]
        if low_att.empty:
            report_lines.append(
                f"  No students with attendance < {attendance_threshold}%."
            )
        else:
            report_lines.append(
                f"  Students with attendance < {attendance_threshold}%:  "
                f"{len(low_att)} student(s)"
            )
            concern_table = low_att[[
                "name", "department", "attendance_pct", "average"
            ]].sort_values("attendance_pct")
            report_lines.append(concern_table.to_string(index=False))
            if export_csv:
                _export_table(concern_table, "low_attendance.csv", output_dir)
    else:
        report_lines.append("  Attendance data not available.")
    report_lines.append("")

    # === SECTION 6: Insights ===============================================
    report_lines.append("6. KEY INSIGHTS")
    report_lines.append(sep_sub)
    insights = _generate_student_insights(df, attendance_threshold)
    for ins in insights:
        report_lines.append(f"  • {ins}")
    report_lines.append("")
    report_lines.append(sep_main)

    full_report = "\n".join(report_lines)
    print(full_report)

    if export_txt:
        _export_text_report(full_report, "student_report.txt", output_dir)
    return full_report


def _generate_student_insights(
    df: pd.DataFrame, attendance_threshold: float
) -> list:
    """Generate plain-language insights for the student report."""
    insights = []
    if "result" in df.columns:
        pass_rate = (df["result"] == "Pass").mean() * 100
        if pass_rate >= 80:
            insights.append(f"Pass rate is strong at {pass_rate:.1f}%.")
        elif pass_rate < 50:
            insights.append(
                f"Pass rate is concerning at {pass_rate:.1f}%. "
                "Recommend targeted interventions."
            )
        else:
            insights.append(
                f"Pass rate is {pass_rate:.1f}%, which is moderate."
            )
    if "attendance_pct" in df.columns:
        low_att_count = int((df["attendance_pct"] < attendance_threshold).sum())
        if low_att_count > 0:
            insights.append(
                f"{low_att_count} student(s) have attendance below "
                f"{attendance_threshold}%."
            )
    if "department" in df.columns and "average" in df.columns:
        best_dept = df.groupby("department")["average"].mean().idxmax()
        worst_dept = df.groupby("department")["average"].mean().idxmin()
        insights.append(
            f"Best performing department: {best_dept}; "
            f"needs improvement: {worst_dept}."
        )
    if "grade" in df.columns:
        a_plus = int((df["grade"] == "A+").sum())
        f_grade = int((df["grade"] == "F").sum())
        insights.append(f"{a_plus} student(s) achieved A+ grade.")
        if f_grade > 0:
            insights.append(f"{f_grade} student(s) received F grade.")
    return insights


# ---------------------------------------------------------------------------
# Sales Report
# ---------------------------------------------------------------------------

def sales_report(
    df: pd.DataFrame,
    export_csv: bool = False,
    export_txt: bool = False,
    output_dir: str = "output",
) -> str:
    """Generate a comprehensive sales analytical report.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned sales DataFrame (expected to have 'revenue', 'order_date').
    export_csv : bool
        If True, save summary tables to CSV.
    export_txt : bool
        If True, save the full report to .txt.
    output_dir : str
        Directory for exports.

    Returns
    -------
    str
        The full report text.
    """
    if df.empty:
        return "[SALES REPORT]\nNo data available."

    sep_main = "═" * 70
    sep_sub = "─" * 70

    report_lines = []
    report_lines.append(sep_main)
    report_lines.append("              BUSINESS SALES ANALYTICAL REPORT")
    report_lines.append(sep_main)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(sep_sub)
    report_lines.append("")

    # Ensure revenue column exists
    if "revenue" not in df.columns:
        if "quantity" in df.columns and "unit_price" in df.columns:
            df = df.copy()
            df["revenue"] = df["quantity"] * df["unit_price"]
        else:
            report_lines.append("Revenue column not available.")
            return "\n".join(report_lines)

    # === SECTION 1: Overall Sales Metrics ==================================
    report_lines.append("1. OVERALL SALES METRICS")
    report_lines.append(sep_sub)
    total_orders = len(df)
    total_revenue = df["revenue"].sum()
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    report_lines.append(f"  Total Orders         : {total_orders}")
    report_lines.append(f"  Total Revenue        : ₹{total_revenue:,.2f}")
    report_lines.append(f"  Average Order Value  : ₹{aov:,.2f}")
    if "quantity" in df.columns:
        total_qty = df["quantity"].sum()
        report_lines.append(f"  Total Quantity Sold  : {int(total_qty)}")
    report_lines.append("")

    # === SECTION 2: Revenue by Region ======================================
    report_lines.append("2. REVENUE BY REGION")
    report_lines.append(sep_sub)
    if "region" in df.columns:
        region_summary = (
            df.groupby("region")
            .agg(
                total_revenue=("revenue", "sum"),
                order_count=("order_id", "count"),
                avg_revenue=("revenue", "mean"),
            )
            .round(2)
            .sort_values("total_revenue", ascending=False)
            .reset_index()
        )
        region_summary.columns = ["Region", "Total Revenue", "Orders", "Avg Revenue"]
        report_lines.append(region_summary.to_string(index=False))
        if export_csv:
            _export_table(region_summary, "revenue_by_region.csv", output_dir)
    else:
        report_lines.append("  Region data not available.")
    report_lines.append("")

    # === SECTION 3: Revenue by Category ====================================
    report_lines.append("3. REVENUE BY CATEGORY")
    report_lines.append(sep_sub)
    if "category" in df.columns:
        cat_summary = (
            df.groupby("category")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        cat_summary.columns = ["Category", "Total Revenue"]
        cat_summary["Total Revenue"] = cat_summary["Total Revenue"].round(2)
        report_lines.append(cat_summary.to_string(index=False))
        if export_csv:
            _export_table(cat_summary, "revenue_by_category.csv", output_dir)
    else:
        report_lines.append("  Category data not available.")
    report_lines.append("")

    # === SECTION 4: Product Performance ====================================
    report_lines.append("4. PRODUCT PERFORMANCE")
    report_lines.append(sep_sub)
    if "product" in df.columns:
        prod_summary = (
            df.groupby("product")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        prod_summary.columns = ["Product", "Total Revenue"]
        prod_summary["Total Revenue"] = prod_summary["Total Revenue"].round(2)
        best_product = prod_summary.iloc[0] if not prod_summary.empty else None
        worst_product = prod_summary.iloc[-1] if not prod_summary.empty else None
        report_lines.append("  Top 5 Products:")
        report_lines.append(prod_summary.head(5).to_string(index=False))
        report_lines.append("")
        report_lines.append(f"  Best Product : {best_product['Product']} "
                            f"(₹{best_product['Total Revenue']:,.2f})")
        report_lines.append(f"  Worst Product: {worst_product['Product']} "
                            f"(₹{worst_product['Total Revenue']:,.2f})")
        if export_csv:
            _export_table(prod_summary, "product_performance.csv", output_dir)
    else:
        report_lines.append("  Product data not available.")
    report_lines.append("")

    # === SECTION 5: Monthly Sales Trend ====================================
    report_lines.append("5. MONTHLY SALES TREND")
    report_lines.append(sep_sub)
    if "order_date" in df.columns:
        df_temp = df.copy()
        df_temp["order_date"] = pd.to_datetime(df_temp["order_date"], errors="coerce")
        df_temp["year_month"] = df_temp["order_date"].dt.to_period("M")
        monthly = (
            df_temp.groupby("year_month")
            .agg(total_revenue=("revenue", "sum"), order_count=("order_id", "count"))
            .reset_index()
        )
        monthly["total_revenue"] = monthly["total_revenue"].round(2)
        monthly = monthly.sort_values("year_month")
        report_lines.append(monthly.to_string(index=False))
        best_month_idx = monthly["total_revenue"].idxmax()
        best_month = monthly.loc[best_month_idx, "year_month"]
        best_revenue = monthly.loc[best_month_idx, "total_revenue"]
        report_lines.append(f"\n  Best Month: {best_month} (₹{best_revenue:,.2f})")
        if export_csv:
            _export_table(monthly, "monthly_sales_trend.csv", output_dir)
    else:
        report_lines.append("  Order date data not available.")
    report_lines.append("")

    # === SECTION 6: Insights ===============================================
    report_lines.append("6. KEY INSIGHTS")
    report_lines.append(sep_sub)
    insights = _generate_sales_insights(df, region_summary if "region" in df.columns else None)
    for ins in insights:
        report_lines.append(f"  • {ins}")
    report_lines.append("")
    report_lines.append(sep_main)

    full_report = "\n".join(report_lines)
    print(full_report)

    if export_txt:
        _export_text_report(full_report, "sales_report.txt", output_dir)
    return full_report


def _generate_sales_insights(df: pd.DataFrame, region_summary: Optional[pd.DataFrame]) -> list:
    """Generate plain-language insights for the sales report."""
    insights = []
    total_revenue = df["revenue"].sum()
    total_orders = len(df)
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    insights.append(
        f"Total revenue of ₹{total_revenue:,.2f} from {total_orders} orders."
    )
    insights.append(f"Average order value is ₹{aov:,.2f}.")
    if region_summary is not None and not region_summary.empty:
        top_region = region_summary.iloc[0]["Region"]
        insights.append(f"Top performing region is {top_region}.")
    if "category" in df.columns:
        cat_counts = df["category"].value_counts()
        if not cat_counts.empty:
            top_cat = cat_counts.idxmax()
            insights.append(f"Most popular category by order count: {top_cat}.")
    return insights


# ---------------------------------------------------------------------------
# Data Quality Report
# ---------------------------------------------------------------------------

def data_quality_report(
    summary_info: Dict[str, Any],
    export_txt: bool = False,
    output_dir: str = "output",
) -> str:
    """Generate a data quality assessment report from cleaning summary.

    Parameters
    ----------
    summary_info : dict
        Dictionary returned by data_cleaning.clean_data().
    export_txt : bool
        If True, save the report to .txt.
    output_dir : str
        Directory for exports.

    Returns
    -------
    str
        The full report text.
    """
    sep_main = "═" * 70
    sep_sub = "─" * 70

    report_lines = []
    report_lines.append(sep_main)
    report_lines.append("                 DATA QUALITY ASSESSMENT REPORT")
    report_lines.append(sep_main)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(sep_sub)
    report_lines.append("")

    # === SECTION 1: Data Completeness ======================================
    report_lines.append("1. DATA COMPLETENESS")
    report_lines.append(sep_sub)
    rows_before = summary_info.get("rows_before", 0)
    rows_after = summary_info.get("rows_after", 0)
    missing_before = summary_info.get("missing_before", 0)
    missing_after = summary_info.get("missing_after", 0)
    report_lines.append(f"  Rows before cleaning     : {rows_before}")
    report_lines.append(f"  Missing values before    : {missing_before}")
    report_lines.append(f"  Rows after cleaning      : {rows_after}")
    report_lines.append(f"  Missing values after     : {missing_after}")
    report_lines.append("")

    # === SECTION 2: Duplicates & ID Conflicts ==============================
    report_lines.append("2. DUPLICATES & ID CONFLICTS")
    report_lines.append(sep_sub)
    exact_dups = summary_info.get("exact_dups_removed", 0)
    id_dups = summary_info.get("id_dup_removed", 0)
    id_conflicts = summary_info.get("id_conflicts", [])
    report_lines.append(f"  Exact duplicate rows removed : {exact_dups}")
    report_lines.append(f"  ID duplicate rows removed    : {id_dups}")
    if id_conflicts:
        report_lines.append(f"  ID conflicts detected        : {len(id_conflicts)}")
        for c in id_conflicts[:5]:
            cols = c.get("conflicting_cols", [])
            if not cols:
                cols = ["(exact duplicate)"]
            report_lines.append(
                f"    ID={c['id']}  ({c['count']} rows)  Conflicting: {cols}"
            )
    else:
        report_lines.append("  No ID conflicts detected.")
    report_lines.append("")

    # === SECTION 3: Invalid Values =========================================
    report_lines.append("3. INVALID / OUT-OF-RANGE VALUES")
    report_lines.append(sep_sub)
    invalid_values = summary_info.get("invalid_values", {})
    if invalid_values:
        report_lines.append("  Columns with out-of-range or non-numeric values:")
        for col, cnt in invalid_values.items():
            report_lines.append(f"    {col:<22}: {cnt} value(s) replaced with NaN")
    else:
        report_lines.append("  No invalid values detected.")
    report_lines.append("")

    # === SECTION 4: Fixes Applied ==========================================
    report_lines.append("4. FIXES APPLIED")
    report_lines.append(sep_sub)
    text_fixes = summary_info.get("text_fixes", 0)
    numeric_imputed = summary_info.get("numeric_imputed", 0)
    text_imputed = summary_info.get("text_imputed", 0)
    num_strategy = summary_info.get("num_strategy", "?")
    text_strategy = summary_info.get("text_strategy", "?")
    report_lines.append(f"  Text cells normalised (strip/case) : {text_fixes}")
    report_lines.append(f"  Numeric cells imputed ({num_strategy:<6})  : {numeric_imputed}")
    report_lines.append(f"  Text cells imputed ({text_strategy:<8})  : {text_imputed}")
    report_lines.append("")

    # === SECTION 5: Quality Insights =======================================
    report_lines.append("5. QUALITY INSIGHTS")
    report_lines.append(sep_sub)
    insights = []
    total_issues = exact_dups + id_dups + missing_before + sum(invalid_values.values())
    if total_issues == 0:
        insights.append("Dataset is clean with no issues detected.")
    else:
        insights.append(f"Total data quality issues detected: {total_issues}.")
        if exact_dups > 0:
            insights.append(f"{exact_dups} exact duplicate row(s) removed.")
        if id_dups > 0:
            insights.append(f"{id_dups} ID duplicate(s) removed.")
        if missing_before > 0:
            insights.append(f"{missing_before} missing value(s) handled.")
        if invalid_values:
            total_invalid = sum(invalid_values.values())
            insights.append(f"{total_invalid} invalid/out-of-range value(s) corrected.")
    for ins in insights:
        report_lines.append(f"  • {ins}")
    report_lines.append("")
    report_lines.append(sep_main)

    full_report = "\n".join(report_lines)
    print(full_report)

    if export_txt:
        _export_text_report(full_report, "data_quality_report.txt", output_dir)
    return full_report


# ---------------------------------------------------------------------------
# Export Helpers
# ---------------------------------------------------------------------------

def _export_table(df: pd.DataFrame, filename: str, output_dir: str) -> None:
    """Export a DataFrame to CSV in output_dir."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    path = out_path / filename
    df.to_csv(path, index=False)
    print(f"  → Exported: {path}")


def _export_text_report(report_text: str, filename: str, output_dir: str) -> None:
    """Export report text to a .txt file."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    path = out_path / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"  → Exported: {path}")

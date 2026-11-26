# Student and Business Data Processing & Analytical Reporting System

## Overview

A modular, console/script-based Python 3.8+ application for processing student academic data and business sales data, performing data cleaning, numerical analysis, and generating analytical reports.

---

## Requirements

| Dependency | Minimum Version | Purpose |
|------------|-----------------|---------|
| Python     | 3.8+            | Runtime |
| NumPy      | 1.21+           | Vectorised numerical analysis |
| Pandas     | 1.3+            | DataFrame operations & analysis |

> **No external analysis libraries, GUI/web frameworks, databases, or ML models** are used.

---

## Setup

### 1. Install dependencies

```bash
pip install numpy pandas
```

### 2. Clone / extract the project

Ensure the following directory structure exists:

```
student_data_processing/
├── main.py
├── data_loader.py
├── data_cleaning.py
├── collections_ops.py
├── numpy_analysis.py
├── pandas_analysis.py
├── reports.py
├── data/
│   ├── students.csv          # Clean student data (18 rows)
│   ├── students_dirty.csv    # Dirty student data (28 rows with issues)
│   ├── sales.csv             # Clean sales data (20 rows)
│   ├── sales_dirty.csv       # Dirty sales data (29 rows with issues)
│   └── departments.csv       # Department lookup (6 rows)
├── output/                   # Auto-created for exports
└── tests/
    ├── README.md
    └── test_log.md
```

---

## Running the Application

Navigate into the project root and run:

```bash
cd student_data_processing
python main.py
```

You will see an interactive text menu. Enter a number and press **Enter**.

### Menu Options

| Option | Description |
|--------|-------------|
| 1  | Load clean student CSV |
| 2  | Load **dirty** student CSV → runs full cleaning pipeline |
| 3  | Python Collections demo (sets, dicts, tuples, sorting) |
| 4  | NumPy numerical analysis demo |
| 5  | Pandas analysis demo (grades, filtering, groupby, pivot tables) |
| 6  | Generate student performance report (optional export) |
| 7  | Generate data quality report from last cleaning run |
| 8  | Load clean sales CSV |
| 9  | Load **dirty** sales CSV → runs full cleaning pipeline |
| 10 | Pandas sales analysis (groupby, pivot, crosstab, monthly trend) |
| 11 | Generate sales analytical report (optional export) |
| 12 | **Full pipeline** – clean data, all steps in sequence |
| 13 | **Full pipeline** – dirty data, all steps in sequence |
| 0  | Exit |

> **Tip:** To see the full end-to-end system, choose **12** (clean) or **13** (dirty).

---

## Features

### Data Loading (`data_loader.py`)
- `load_csv()` — Load any CSV with graceful `FileNotFoundError` and `EmptyDataError` handling
- Required-column validation with warnings (non-crashing)
- `dataframe_from_dicts()` — Build DataFrames from lists of dicts
- Auto-display of shape, columns, dtypes, first 5 rows

### Python Collections (`collections_ops.py`)
- Student records stored as `list[dict]`
- Constants (subjects, grade boundaries, thresholds) stored as `tuple`
- `unique_values()` — Uses Python `set`
- `count_frequency()` — `dict`-based frequency map
- Set operations: union, intersection, difference (CSE vs good attendance)
- `sort_by_key()` — `sorted()` + `lambda` on list of dicts

### Data Cleaning (`data_cleaning.py`)
- `missing_report()` — Counts + percentages before cleaning
- Out-of-range value detection: marks outside `[0, 100]`, negative quantities
- Non-numeric coercion via `pd.to_numeric(..., errors="coerce")`
- Text standardisation: `.str.strip()` + `.str.title()`
- Exact duplicate removal (`keep="first"`)
- Duplicate ID detection with conflict reporting
- `clean_data()` — Configurable imputation: `"mean"`, `"median"`, or `"zero"` for numeric; `"Unknown"` or `"drop"` for text
- Printed `CLEANING SUMMARY` with before/after stats

### NumPy Analysis (`numpy_analysis.py`)
- `extract_marks_array()` — Converts DataFrame columns to `ndarray` with metadata
- `numpy_statistics()` — mean, median, std, variance, min, max, percentiles (25/50/75)
- `row_wise_ops()` — total/average per student (axis=1, vectorised)
- `column_wise_ops()` — subject stats (axis=0)
- `find_failing_scores()` — Boolean masking (`< pass_mark`)
- `apply_grace_marks()` — `np.clip()` for capped grace
- `pass_fail_labels()` — `np.where()` for labels
- `rank_students()` — `np.argsort()` for ranking

### Pandas Analysis (`pandas_analysis.py`)
- `create_total_marks_series()` — `pd.Series` indexed by student name
- `assign_grades()` — `pd.cut()` for grade bins, computed total/average/percentage/result
- `print_overview()` — `.info()`, `.describe()`, `.head()`, `.tail()`
- `rename_reorder_drop()` — Column manipulation utilities
- `merge_students_departments()` — Left join with departments lookup
- `filter_students()` — Flexible keyword filters: exact, `_min`, `_max`, `_in`, `_contains`
- `filter_or()` — OR-logic filtering
- `sort_data()` — Multi-column sort, top N / bottom N, rank column
- `group_summary()` — Groupby with agg dict
- `grade_distribution()` / `value_counts_analysis()` — Distribution tables
- `sales_pivot()` — `pd.pivot_table()` revenue by region × category
- `crosstab_region_category()` — `pd.crosstab()`
- `monthly_sales_trend()` — Datetime conversion + monthly groupby

### Reports (`reports.py`)
- `student_report()` — Title, date, overall stats, department summary, top/bottom 5, grade distribution, attendance concerns, plain-language insights
- `sales_report()` — Total orders, revenue, AOV, region/category/product breakdown, monthly trend, best/worst product, best month
- `data_quality_report()` — Missing values, duplicates, ID conflicts, invalid values, fixes, quality insights
- Optional CSV and `.txt` exports to `output/`
- Empty DataFrame handling ("No data available")

---

## Data Files

### `data/students.csv` / `data/students_dirty.csv`
- Columns: `student_id`, `name`, `department`, `gender`, `maths`, `science`, `english`, `attendance_pct`, `city`
- Dirty version includes: exact duplicates, duplicate IDs with conflicting values, missing values, out-of-range marks (>100, <0), non-numeric marks (`"abc"`), inconsistent casing/whitespace

### `data/sales.csv` / `data/sales_dirty.csv`
- Columns: `order_id`, `product`, `category`, `region`, `quantity`, `unit_price`, `order_date`
- Revenue is derived as `quantity × unit_price`
- Dirty version includes: exact duplicates, duplicate IDs with date conflicts, missing columns, negative quantities, non-numeric quantities, inconsistent casing/whitespace

### `data/departments.csv`
- Columns: `department`, `HOD`, `building`
- Lookup table for student → department merge

---

## Output Files

After exporting, the `output/` directory contains:

| File | Contents |
|------|----------|
| `student_report.txt` | Full student performance report |
| `sales_report.txt` | Full sales analytical report |
| `data_quality_report.txt` | Data quality assessment |
| `department_summary.csv` | Department-wise summary table |
| `top_students.csv` | Top 5 students |
| `bottom_students.csv` | Bottom 5 students |
| `grade_distribution.csv` | Grade counts & percentages |
| `low_attendance.csv` | Students with attendance < 75% |
| `revenue_by_region.csv` | Region-wise revenue |
| `revenue_by_category.csv` | Category-wise revenue |
| `product_performance.csv` | Product revenue ranking |
| `monthly_sales_trend.csv` | Month-by-month sales |

---

## Architecture

```
main.py  (orchestration / CLI menu)
   ├── data_loader.py       (I/O layer)
   ├── data_cleaning.py     (validation + imputation)
   ├── collections_ops.py   (pure Python collections)
   ├── numpy_analysis.py    (NumPy vectorised analysis)
   ├── pandas_analysis.py   (Pandas transformation & analysis)
   └── reports.py           (formatted output + export)
```

All modules are stateless (functions only). `main.py` holds a lightweight `_state` dict for the pipeline session. Original loaded DataFrames are **never** mutated — every cleaning/transformation step works on a `.copy()`.

---

## Author

MCA Lab Project — Student and Business Data Processing & Analytical Reporting System

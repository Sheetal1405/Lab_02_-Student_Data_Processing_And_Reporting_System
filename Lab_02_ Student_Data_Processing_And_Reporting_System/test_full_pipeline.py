"""Full pipeline test including export and dirty data."""
import data_loader as dl
import data_cleaning as dc
import collections_ops as co
import numpy_analysis as na
import pandas_analysis as pa
import reports as rp

print('\n' + '>'*60)
print('FULL PIPELINE TEST -- DIRTY DATA')
print('>'*60)

# Student dirty pipeline
print('\n--- Loading dirty students ---')
df_dirty = dl.load_csv('data/students_dirty.csv', verbose=False)
print('Loaded:', df_dirty.shape)

dc.missing_report(df_dirty, label='Dirty Students')
clean_df, summary = dc.clean_data(df_dirty, dataset_type='student', num_strategy='median')

print('\n--- Collections Demo ---')
records = co.records_from_dataframe(clean_df)
co.print_collections_demo(records)

print('\n--- NumPy Demo ---')
na.print_numpy_analysis_demo(clean_df)

print('\n--- Pandas Demo ---')
graded = pa.assign_grades(clean_df)
series = pa.create_total_marks_series(clean_df)
print('\nFilter: attendance < 75')
pa.filter_students(graded, attendance_pct_max=74.9)
print('\nSort: Top 5 by total')
top5 = pa.sort_data(graded, columns='total', ascending=False, top_n=5)
print(top5[['name','total','grade']].to_string(index=False))

# Grade distribution
gdist = pa.grade_distribution(graded)
print('\nGrade Distribution:')
print(gdist.to_string(index=False))

# Reports
rp.student_report(graded, export_csv=True, export_txt=True, output_dir='output')
rp.data_quality_report(summary, export_txt=True, output_dir='output')

# Sales dirty pipeline
print('\n--- Loading dirty sales ---')
df_sales = dl.load_csv('data/sales_dirty.csv', verbose=False)
clean_sales, sales_summary = dc.clean_data(df_sales, dataset_type='sales')
clean_sales = pa.add_revenue_column(clean_sales)

pa.sales_group_analysis(clean_sales)
pivot = pa.sales_pivot(clean_sales)
if pivot is not None:
    print('\nPivot table (Revenue by Region x Category):')
    print(pivot.to_string())
ct = pa.crosstab_region_category(clean_sales)
if ct is not None:
    print('\nCrosstab:')
    print(ct.to_string())
monthly = pa.monthly_sales_trend(clean_sales)
print('\nMonthly trend:')
print(monthly.to_string(index=False))

rp.sales_report(clean_sales, export_csv=True, export_txt=True, output_dir='output')

print('\n' + '>'*60)
print('ALL TESTS COMPLETED SUCCESSFULLY')
print('>'*60)

import data_loader as dl
import data_cleaning as dc
import pandas_analysis as pa
import reports as rp

df = dl.load_csv('data/students.csv', verbose=False)
clean_df, summary = dc.clean_data(df, dataset_type='student', num_strategy='median')
graded = pa.assign_grades(clean_df)

print('=== Student Report (abbreviated) ===')
report_text = rp.student_report(graded, export_csv=False, export_txt=False)
# Report already printed by function

print('\n=== Data Quality Report ===')
rp.data_quality_report(summary, export_txt=False)

print('\n=== Sales Report Test ===')
sales_df = dl.load_csv('data/sales.csv', verbose=False)
sales_clean, _ = dc.clean_data(sales_df, dataset_type='sales')
sales_clean = pa.add_revenue_column(sales_clean)
rp.sales_report(sales_clean, export_csv=False, export_txt=False)

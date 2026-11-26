import data_loader as dl
import data_cleaning as dc
import numpy_analysis as na
import pandas_analysis as pa

df = dl.load_csv('data/students.csv', verbose=False)
clean_df, _ = dc.clean_data(df, dataset_type='student', num_strategy='median')

print('=== NumPy Analysis ===')
arr = na.extract_marks_array(clean_df, verbose=True)
overall = na.numpy_statistics(arr)
print(f"\nMean: {overall['mean']:.2f}, Median: {overall['median']:.2f}, Std: {overall['std']:.2f}")

totals, averages = na.row_wise_ops(arr)
print(f"\nRow-wise: First 3 totals = {totals[:3]}")

col_stats = na.column_wise_ops(arr, ['maths', 'science', 'english'])
print(f"\nColumn-wise:")
for subj, stats in col_stats.items():
    print(f"  {subj}: mean={stats['mean']:.2f}, max={stats['max']:.2f}")

failing, fail_count = na.find_failing_scores(arr, pass_mark=35.0)
print(f"\nFailing cells count: {fail_count}")

grace_arr = na.apply_grace_marks(arr, grace=5.0, cap=100.0)
print(f"Grace sample: before={arr[0]}, after={grace_arr[0]}")

labels = na.pass_fail_labels(totals, threshold=105.0)
print(f"Pass count: {sum(labels == 'Pass')}")

ranked = na.rank_students(totals, ascending=False)
print(f"Top 5 ranked indices: {ranked[:5]}")
print(f"Top 5 totals: {totals[ranked[:5]]}")

print('\n=== Pandas Analysis ===')
graded = pa.assign_grades(clean_df)
print(f"Grades assigned: {graded['grade'].value_counts().to_dict()}")

print('\nFilter: CSE students with average > 85')
filtered = pa.filter_students(graded, department='Cse', average_min=85)

print('\nTop 5 by total:')
top5 = pa.sort_data(graded, columns='total', ascending=False, top_n=5)
print(top5[['name', 'total', 'grade']].to_string(index=False))

print('\nDepartment summary:')
dept_sum = pa.group_summary(
    graded, by='department',
    aggregations={'total': 'mean', 'attendance_pct': 'mean'},
    label='Dept Summary'
)

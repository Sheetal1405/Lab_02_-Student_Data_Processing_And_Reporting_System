import data_loader as dl
import data_cleaning as dc
import collections_ops as co

df = dl.load_csv('data/students.csv', verbose=False)
clean_df, _ = dc.clean_data(df, dataset_type='student', num_strategy='median')
records = co.records_from_dataframe(clean_df)

print('=== TC-27: Unique departments ===')
print(co.unique_values(records, 'department'))

print('\n=== TC-28: Freq count ===')
print(co.count_frequency([r['department'] for r in records]))

print('\n=== Set operations ===')
ops = co.set_operations(records, dept_filter='Cse')
print('CSE students:', sorted(ops['dept_set']))
print('Good attendance:', len(ops['attendance_set']), 'students')
print('Intersection:', sorted(ops['intersection']))

print('\n=== Sort by total_marks (top 5) ===')
enriched = co.enrich_records(records)
top5 = co.sort_by_key(enriched, 'total_marks', ascending=False, top_n=5)
for r in top5:
    print(f"  {r['name']:<20} total={r['total_marks']}")

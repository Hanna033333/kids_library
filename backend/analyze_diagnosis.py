import json

with open('diagnosis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== TIME INFO ===")
print(f"Week number: {data['time_info']['week_number']}")
print(f"Age offset: {data['time_info']['age_offset']}")
print(f"Research offset: {data['time_info']['research_offset']}")
print()

print("=== AGE GROUPS ===")
for group_name, group_data in data['age_groups'].items():
    print(f"\n{group_name}:")
    print(f"  Total count: {group_data['total_count']}")
    print(f"  Books in range (offset {data['time_info']['age_offset']} to {data['time_info']['age_offset']+6}): {group_data['books_in_range']}")
    print(f"  Has data: {group_data['has_data']}")
    print(f"  Offset exceeds total: {group_data['offset_exceeds_total']}")
    if group_data.get('sample_books'):
        print(f"  Sample books:")
        for book in group_data['sample_books']:
            print(f"    - ID {book['id']}: {book['title']}")

print("\n=== RESEARCH COUNCIL ===")
rc = data['research_council']
print(f"Total count: {rc['total_count']}")
print(f"Books in range (offset {data['time_info']['research_offset']} to {data['time_info']['research_offset']+6}): {rc['books_in_range']}")
print(f"Has data: {rc['has_data']}")
print(f"Offset exceeds total: {rc['offset_exceeds_total']}")

print("\n=== SONGPA LIBRARY ===")
sp = data['songpa_library']
print(f"Total count: {sp['total_count']}")
print(f"Has data: {sp['has_data']}")
if sp.get('sample_data'):
    print("Sample data:")
    for item in sp['sample_data'][:3]:
        print(f"  - Book ID {item['book_id']}: {item['library_name']} - {item['callno']}")

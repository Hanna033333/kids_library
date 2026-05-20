from supabase_client import supabase
import sys

sys.stdout.reconfigure(encoding='utf-8')

TAXONOMY_TAGS = [
    "#잠자리", "#감정조절", "#자존감", "#사회성", "#인체",
    "#판타지", "#환경보호", "#생명존중", "#가족사랑", "#배려",
    "#모험", "#전래동화", "#예술감성", "#자연관찰", "#역사이야기",
    "#과학원리", "#다양성", "#적응", "#우리문화", "#계절"
]

print("--- 📊 AI 큐레이션 카테고리별 도서 분포 분석 ---")

# Fetch all books with curation_tag in database (with pagination to bypass 1000 limit)
books = []
page_size = 1000
start = 0
while True:
    result = supabase.table("childbook_items")\
        .select("id, title, curation_tag, confidence_score")\
        .not_.is_("curation_tag", "null")\
        .filter("confidence_score", "gt", 0)\
        .range(start, start + page_size - 1)\
        .execute()
    if not result.data:
        break
    books.extend(result.data)
    if len(result.data) < page_size:
        break
    start += page_size

tag_counts = {tag: 0 for tag in TAXONOMY_TAGS}
tag_high_confidence = {tag: 0 for tag in TAXONOMY_TAGS} # confidence_score >= 90

for book in books:
    tags_str = book.get("curation_tag", "")
    if not tags_str:
        continue
    
    # Split by comma
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    confidence = book.get("confidence_score", 0) or 0
    
    for tag in tags:
        if tag in tag_counts:
            tag_counts[tag] += 1
            if confidence >= 90:
                tag_high_confidence[tag] += 1

print(f"총 태깅된 도서 수: {len(books)}권\n")
print(f"{'카테고리 태그':<10} | {'전체 도서 수':<8} | {'신뢰도 90+ 도서':<10} | {'7-Book Rule 충족 여부'}")
print("-" * 70)

satisfied_count = 0
for tag in TAXONOMY_TAGS:
    count = tag_counts[tag]
    high_conf = tag_high_confidence[tag]
    satisfied = "✅ 충족" if count >= 7 else "❌ 미달"
    if count >= 7:
        satisfied_count += 1
    print(f"{tag:<12} | {count:<10} | {high_conf:<12} | {satisfied}")

print("-" * 70)
print(f"20개 카테고리 중 충족된 섹션 수: {satisfied_count}/20")

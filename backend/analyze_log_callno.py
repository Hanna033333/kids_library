import re

def analyze_log():
    """로그에서 청구기호 분석"""
    with open('rescrape_log_20260105_134019.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 청구기호 패턴: [번호] 제목 -> 청구기호
    pattern = r'\[\d+\] (.+?) -> (.+?)(?:\n|$)'
    matches = re.findall(pattern, content)
    
    total_found = 0
    without_prefix = []
    with_prefix = 0
    
    for title, callno in matches:
        if callno == "STILL NOT FOUND":
            continue
        
        total_found += 1
        
        # "아", "유"로 시작하는지 확인
        if not (callno.startswith('아 ') or callno.startswith('유 ')):
            without_prefix.append({
                'title': title,
                'callno': callno
            })
        else:
            with_prefix += 1
    
    print(f"📊 청구기호 분석 결과")
    print(f"=" * 60)
    print(f"총 발견: {total_found}권")
    print(f"'아', '유' 있음: {with_prefix}권")
    print(f"'아', '유' 없음: {len(without_prefix)}권")
    print(f"")
    
    if without_prefix:
        print(f"⚠️  '아', '유' 없는 청구기호 목록:")
        print(f"=" * 60)
        for i, book in enumerate(without_prefix, 1):
            print(f"{i}. {book['title']}")
            print(f"   청구기호: {book['callno']}")
            print()

if __name__ == "__main__":
    analyze_log()

"""
중복 청구기호를 가진 책들에 대해 웹사이트 크롤링 테스트
"""
from supabase_client import supabase
from crawler import get_series_number_from_website
from collections import defaultdict
import time

print("=" * 60)
print("권차 기호 크롤링 테스트")
print("=" * 60)
print()

try:
    # 중복 청구기호 찾기
    print("1. 중복 청구기호 찾기...")
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        data = supabase.table("library_items").select("*").range(offset, offset + page_size - 1).execute()
        if not data.data or len(data.data) == 0:
            break
        all_data.extend(data.data)
        offset += page_size
        if len(data.data) < page_size:
            break
    
    # 청구기호별로 그룹화
    callno_groups = defaultdict(list)
    for item in all_data:
        callno = item.get('callno', '')
        if callno:
            # 권차 기호 제외한 기본 청구기호 추출
            base_callno = callno
            if '-' in callno:
                parts = callno.rsplit('-', 1)
                if len(parts) == 2 and parts[1].isdigit():
                    base_callno = parts[0]
            
            callno_groups[base_callno].append({
                'isbn13': item.get('isbn13', ''),
                'title': item.get('title', ''),
                'author': item.get('author', ''),
                'callno': callno,
            })
    
    # 중복이 있는 그룹 찾기
    duplicate_groups = {k: v for k, v in callno_groups.items() if len(v) >= 2}
    
    print(f"   중복 청구기호 그룹: {len(duplicate_groups)}개")
    print(f"   테스트 대상 도서 수: {sum(len(v) for v in duplicate_groups.values())}권")
    print()
    
    # 테스트 실행 (각 그룹에서 최대 2권씩)
    print("2. 크롤링 테스트 시작...")
    print("-" * 60)
    
    test_results = []
    total_tested = 0
    total_success = 0
    total_failed = 0
    
    for base_callno, books in sorted(duplicate_groups.items()):
        # 각 그룹에서 최대 2권씩 테스트
        test_books = books[:2]
        
        for book in test_books:
            total_tested += 1
            isbn13 = book['isbn13']
            title = book['title']
            current_callno = book['callno']
            
            print(f"\n[{total_tested}] {title[:40]}")
            print(f"    ISBN: {isbn13}")
            print(f"    현재 청구기호: {current_callno}")
            print(f"    기본 청구기호: {base_callno}")
            
            start_time = time.time()
            try:
                series_number = get_series_number_from_website(isbn13, title, base_callno)
                elapsed_time = time.time() - start_time
                
                if series_number:
                    total_success += 1
                    print(f"    ✅ 성공! 권차 기호: {series_number} (소요 시간: {elapsed_time:.2f}초)")
                    test_results.append({
                        'isbn13': isbn13,
                        'title': title,
                        'base_callno': base_callno,
                        'current_callno': current_callno,
                        'series_number': series_number,
                        'success': True,
                        'elapsed_time': elapsed_time
                    })
                else:
                    total_failed += 1
                    print(f"    ❌ 실패: 권차 기호를 찾을 수 없음 (소요 시간: {elapsed_time:.2f}초)")
                    test_results.append({
                        'isbn13': isbn13,
                        'title': title,
                        'base_callno': base_callno,
                        'current_callno': current_callno,
                        'series_number': '',
                        'success': False,
                        'elapsed_time': elapsed_time
                    })
            except Exception as e:
                total_failed += 1
                elapsed_time = time.time() - start_time
                print(f"    ❌ 오류: {e} (소요 시간: {elapsed_time:.2f}초)")
                test_results.append({
                    'isbn13': isbn13,
                    'title': title,
                    'base_callno': base_callno,
                    'current_callno': current_callno,
                    'series_number': '',
                    'success': False,
                    'error': str(e),
                    'elapsed_time': elapsed_time
                })
            
            # API 부하 방지를 위한 대기
            time.sleep(1)
    
    print()
    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print()
    
    success_rate = (total_success / total_tested * 100) if total_tested > 0 else 0
    avg_time = sum(r['elapsed_time'] for r in test_results) / len(test_results) if test_results else 0
    
    print(f"총 테스트: {total_tested}권")
    print(f"성공: {total_success}권")
    print(f"실패: {total_failed}권")
    print(f"성공률: {success_rate:.1f}%")
    print(f"평균 소요 시간: {avg_time:.2f}초")
    print()
    
    if success_rate >= 80:
        print("✅ 성공률 80% 이상 - 크롤링 구현 가능")
    else:
        print("⚠️ 성공률 80% 미만 - 수동 처리 고려 필요")
    
    print()
    print("=" * 60)
    print("상세 결과")
    print("=" * 60)
    print()
    
    for i, result in enumerate(test_results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{i}. {status} {result['title'][:40]}")
        print(f"   기본 청구기호: {result['base_callno']}")
        if result['success']:
            print(f"   권차 기호: {result['series_number']}")
            print(f"   완성된 청구기호: {result['base_callno']}-{result['series_number']}")
        else:
            print(f"   실패")
        print(f"   소요 시간: {result['elapsed_time']:.2f}초")
        print()

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()







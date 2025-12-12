"""
childbook_items에서 ISBN 또는 pangyo_callno가 없는 항목에 대해 네이버 책검색 API와 알라딘 Open API로 ISBN 검색 및 채우기
"""
from supabase_client import supabase
from library_api import search_isbn_combined
import time
import sys
from datetime import datetime

# 로그 파일 설정
log_file = open("fill_isbn_log.txt", "w", encoding="utf-8")

def log_print(*args, **kwargs):
    """콘솔과 로그 파일에 동시에 출력"""
    message = " ".join(str(arg) for arg in args)
    print(message, **kwargs)
    log_file.write(message + "\n")
    log_file.flush()

log_print("=" * 60)
log_print("childbook_items에 ISBN 채우기 (네이버 + 알라딘 API)")
log_print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_print("=" * 60)
log_print()

# 1) childbook_items에서 ISBN과 pangyo_callno 둘 다 없는 항목 조회
log_print("1. ISBN과 pangyo_callno 둘 다 없는 항목 조회 중...")
try:
    # 전체 데이터를 페이지별로 가져오기
    child_items = []
    page = 0
    page_size = 1000
    
    while True:
        log_print(f"   페이지 {page + 1} 조회 중...")
        res = supabase.table("childbook_items").select("*").range(page * page_size, (page + 1) * page_size - 1).execute()
        if not res.data:
            break
        
        log_print(f"   페이지 {page + 1}: {len(res.data)}개 항목 조회됨, 필터링 중...")
        
        # ISBN과 pangyo_callno 둘 다 없는 항목만 필터링
        page_missing_count = 0
        for item in res.data:
            isbn = item.get("isbn")
            pangyo_callno = item.get("pangyo_callno")
            
            # ISBN이 없거나 빈 문자열인지 확인
            has_isbn = isbn and len(str(isbn).strip()) > 0
            # pangyo_callno가 없거나 빈 문자열인지 확인
            has_pangyo_callno = pangyo_callno and len(str(pangyo_callno).strip()) > 0
            
            # 둘 다 없는 경우만 추가
            if not has_isbn and not has_pangyo_callno:
                child_items.append(item)
                page_missing_count += 1
        
        log_print(f"   페이지 {page + 1}: {page_missing_count}개 항목이 처리 대상 (누적: {len(child_items)}개)")
        
        if len(res.data) < page_size:
            break
        page += 1
    
    log_print(f"   [OK] ISBN과 pangyo_callno 둘 다 없는 항목: {len(child_items):,}개")
except Exception as e:
    log_print(f"   [ERROR] 오류: {e}")
    log_file.close()
    sys.exit(1)

if len(child_items) == 0:
    log_print("\n[OK] 모든 항목에 ISBN과 pangyo_callno가 이미 있습니다!")
    log_file.close()
    sys.exit(0)

log_print()

# 2) 각 항목에 대해 네이버 + 알라딘 API로 ISBN 검색
log_print("2. 네이버 + 알라딘 API로 ISBN 검색 중...")
log_print("   [INFO] API 호출 제한을 고려하여 요청 간 딜레이를 둡니다.")
log_print(f"   [INFO] 총 {len(child_items):,}개 항목 처리 예정")
log_print()

success_count = 0
fail_count = 0
skip_count = 0
aladin_success = 0
naver_success = 0

for idx, item in enumerate(child_items):
    item_id = item.get("id")
    title = item.get("title", "").strip()
    author_raw = item.get("author", "").strip()
    
    if not title:
        skip_count += 1
        if skip_count <= 5:
            log_print(f"   [SKIP] ID {item_id}: 제목이 없어서 건너뜀")
        continue
    
    # 저자 정보 정리 (복잡한 형식 처리)
    # 예: "사노 요코 글, 그림 | 김난주 옮김" -> "사노 요코"
    author = None
    if author_raw:
        # 파이프(|)로 구분된 경우 첫 번째 저자만 사용
        author_parts = author_raw.split("|")
        first_author = author_parts[0].strip()
        # "글", "그림", "옮김" 등의 단어 제거
        author_clean = first_author.replace("글", "").replace("그림", "").replace("옮김", "").replace(",", "").strip()
        # 쉼표로 구분된 경우 첫 번째 저자만 사용 (예: "니콜라이 포포프, 레이먼드 브릭스" -> "니콜라이 포포프")
        if "," in author_clean:
            author_clean = author_clean.split(",")[0].strip()
        if author_clean:
            author = author_clean
    
    try:
        # 통합 검색 함수 사용 (알라딘 + 네이버)
        isbn, score, source = search_isbn_combined(title, author)
        
        # 제목만으로 재시도 (저자 포함 검색이 실패한 경우)
        if not isbn or score < 30:
            isbn, score, source = search_isbn_combined(title, None)
        
        if isbn and score >= 30:  # 유사도 30점 이상으로 낮춤
            # Supabase에 업데이트
            try:
                supabase.table("childbook_items").update({
                    "isbn": isbn
                }).eq("id", item_id).execute()
                success_count += 1
                if source == 'aladin':
                    aladin_success += 1
                elif source == 'naver':
                    naver_success += 1
            except Exception as e:
                log_print(f"   [ERROR] ID {item_id} 업데이트 실패: {e}")
                fail_count += 1
        else:
            fail_count += 1
            if fail_count <= 5:
                log_print(f"   [WARN] ID {item_id}: ISBN을 찾지 못함 (유사도: {score})")
        
        # 진행 상황 출력 (5개마다)
        if (idx + 1) % 5 == 0:
            log_print(f"   진행 중: {idx + 1}/{len(child_items)} (성공: {success_count}, 실패: {fail_count}, 건너뜀: {skip_count})")
            log_print(f"            알라딘: {aladin_success}개, 네이버: {naver_success}개")
        
        # API 호출 제한 고려 (초당 1회 정도)
        time.sleep(0.1)
        
    except Exception as e:
        fail_count += 1
        if fail_count <= 5:
            log_print(f"   [ERROR] ID {item_id} 처리 중 오류: {e}")

log_print()
log_print("=" * 60)
log_print("[OK] 완료!")
log_print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_print("-" * 60)
log_print(f"총 처리: {len(child_items)}개")
log_print(f"성공: {success_count}개")
log_print(f"  - 알라딘 API: {aladin_success}개")
log_print(f"  - 네이버 API: {naver_success}개")
log_print(f"실패: {fail_count}개")
log_print(f"건너뜀: {skip_count}개")
log_print("=" * 60)
log_file.close()


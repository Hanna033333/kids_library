"""
100권씩 수집하고 각 배치 완료 시 알림 (출력 표시)
"""
from main import sync_library_books_child
from crawler import fetch_library_books_child
from supabase_client import supabase
import time
from datetime import datetime
import sys

def collect_in_batches(start_dt: str = "2010-01-01", end_dt: str = "2025-12-31", batch_size: int = 100):
    """
    100권씩 수집하고 각 배치 완료 시 알림
    """
    print("=" * 60)
    print("판교 도서관 아동 도서 수집 (100권씩 배치 처리)")
    print(f"기간: {start_dt} ~ {end_dt}")
    print("=" * 60)
    print()
    sys.stdout.flush()
    
    # 현재 저장된 데이터 수 확인
    try:
        existing = supabase.table("library_items").select("*", count="exact").execute()
        count_before = existing.count if hasattr(existing, 'count') else len(existing.data) if existing.data else 0
        print(f"현재 library_items에 저장된 도서 수: {count_before:,}권")
    except Exception as e:
        print(f"기존 데이터 확인 중 오류: {e}")
        count_before = 0
    
    # 현재 저장된 데이터 수로 시작 페이지 추정
    # 1000페이지까지 데이터가 확인되었으므로, 대략 950페이지부터 시작
    # 또는 저장된 데이터 수를 기준으로 추정 (페이지당 평균 30-35권)
    estimated_start_page = 460
    if count_before > 0:
        # 페이지당 평균 30-35권의 아동 도서가 있다고 가정
        estimated_start_page = max(460, min(950, count_before // 35))
        print(f"추정 시작 페이지: {estimated_start_page} (1000페이지까지 데이터 확인됨)")
    else:
        print(f"시작 페이지: {estimated_start_page}")
    print()
    
    print()
    print(f"⚠️  {batch_size}권씩 수집하고 각 배치 완료 시 알림을 드립니다.")
    print()
    sys.stdout.flush()
    
    start_time = time.time()
    total_collected = 0
    batch_number = 1
    
    # 크롤러에서 직접 데이터 가져오기 (페이지 단위로)
    # 추정된 시작 페이지부터 이어서 시작
    page = estimated_start_page
    page_size = 100  # 페이지 크기
    batch_books = []
    
    url = "http://data4library.kr/api/itemSrch"
    from crawler import DATA4LIBRARY_KEY, PANGYO_CODE
    import requests
    
    while True:
        params = {
            "authKey": DATA4LIBRARY_KEY,
            "libCode": PANGYO_CODE,
            "startDt": start_dt,
            "endDt": end_dt,
            "pageNo": page,
            "pageSize": page_size,
            "format": "json"
        }
        
        try:
            res = requests.get(url, params=params, timeout=120)
            res.raise_for_status()
            
            if not res.text:
                print(f"{page} 페이지: 빈 응답 - 수집 종료")
                sys.stdout.flush()
                break
                
            try:
                data = res.json()
            except ValueError as json_err:
                print(f"{page} 페이지: JSON 파싱 오류 - {json_err}")
                sys.stdout.flush()
                break
                
        except requests.exceptions.RequestException as e:
            print(f"요청 오류 발생: {e}")
            sys.stdout.flush()
            break
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
            sys.stdout.flush()
            break
        
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            print(f"{page} 페이지: 더 이상 데이터 없음 - 수집 종료")
            sys.stdout.flush()
            break
        
        # 아동 도서만 필터링하여 배치에 추가
        for d in docs:
            item = d.get("doc", {})
            class_no = item.get("class_no", "")
            call_numbers = item.get("callNumbers", [])
            
            # 아동 도서인지 확인
            is_child = False
            actual_callno = None
            
            for call_info in call_numbers:
                call_number = call_info.get("callNumber", {})
                separate_shelf_name = call_number.get("separate_shelf_name", "")
                shelf_loc_name = call_number.get("shelf_loc_name", "")
                book_code = call_number.get("book_code", "")
                copy_code = call_number.get("copy_code", "")
                
                if (separate_shelf_name and (separate_shelf_name.startswith('아') or separate_shelf_name.startswith('유'))) or \
                   ('어린이' in shelf_loc_name):
                    is_child = True
                    # 전체 청구기호 구성
                    parts = []
                    if separate_shelf_name:
                        parts.append(separate_shelf_name)
                    if class_no:
                        parts.append(class_no)
                    if book_code:
                        parts.append(book_code)
                    if copy_code:
                        parts.append(copy_code)
                    
                    if len(parts) >= 3:
                        actual_callno = f"{parts[0]} {parts[1]}-{parts[2]}"
                        if len(parts) >= 4:
                            actual_callno += f"-{parts[3]}"
                    elif len(parts) == 2:
                        actual_callno = f"{parts[0]} {parts[1]}"
                    elif len(parts) == 1:
                        actual_callno = parts[0]
                    break
            
            if not is_child or not actual_callno:
                continue
            
            batch_books.append({
                "isbn13": item.get("isbn13", ""),
                "title": item.get("bookname", ""),
                "author": item.get("authors", ""),
                "callno": actual_callno,
                "lib_code": PANGYO_CODE,
            })
            
            # 배치 크기에 도달하면 저장
            if len(batch_books) >= batch_size:
                # Supabase에 저장
                try:
                    for b in batch_books:
                        book_data = {
                            "isbn13": b["isbn13"],
                            "title": b["title"],
                            "author": b["author"],
                            "callno": b["callno"],
                            "lib_code": b["lib_code"],
                        }
                        supabase.table("library_items").upsert(book_data).execute()
                    
                    total_collected += len(batch_books)
                    elapsed = time.time() - start_time
                    
                    print(f"\n{'='*60}")
                    print(f"✅ 배치 #{batch_number} 완료!")
                    print(f"   현재 페이지: {page}")
                    print(f"   수집된 도서: {len(batch_books)}권")
                    print(f"   누적 수집: {total_collected}권")
                    print(f"   소요 시간: {elapsed:.2f}초 ({elapsed/60:.2f}분)")
                    print(f"{'='*60}\n")
                    sys.stdout.flush()
                    
                    batch_number += 1
                    batch_books = []
                    
                    # API 부하 방지를 위한 짧은 대기
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ 배치 #{batch_number} 저장 중 오류: {e}")
                    sys.stdout.flush()
                    batch_books = []
                    continue
        
        print(f"{page} 페이지 완료 / 현재 배치: {len(batch_books)}권")
        sys.stdout.flush()
        page += 1
        
        # API 부하 방지를 위한 짧은 대기
        time.sleep(0.5)
    
    # 남은 도서 저장
    if batch_books:
        try:
            for b in batch_books:
                book_data = {
                    "isbn13": b["isbn13"],
                    "title": b["title"],
                    "author": b["author"],
                    "callno": b["callno"],
                    "lib_code": b["lib_code"],
                }
                supabase.table("library_items").upsert(book_data).execute()
            
            total_collected += len(batch_books)
            elapsed = time.time() - start_time
            
            print(f"\n{'='*60}")
            print(f"✅ 마지막 배치 완료!")
            print(f"   수집된 도서: {len(batch_books)}권")
            print(f"   누적 수집: {total_collected}권")
            print(f"   소요 시간: {elapsed:.2f}초 ({elapsed/60:.2f}분)")
            print(f"{'='*60}\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ 마지막 배치 저장 중 오류: {e}")
            sys.stdout.flush()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print()
    print("=" * 60)
    print(f"✅ 전체 수집 및 저장 완료!")
    print(f"총 수집된 도서 수: {total_collected}권")
    print(f"총 소요 시간: {elapsed_time:.2f}초 ({elapsed_time/60:.2f}분, {elapsed_time/3600:.2f}시간)")
    print("=" * 60)
    sys.stdout.flush()
    
    # 저장 후 데이터 수 확인
    try:
        updated = supabase.table("library_items").select("*", count="exact").execute()
        count_after = updated.count if hasattr(updated, 'count') else len(updated.data) if updated.data else 0
        print(f"\n저장 후 library_items에 저장된 도서 수: {count_after}권")
        print(f"추가된 도서 수: {count_after - count_before}권")
        sys.stdout.flush()
    except Exception as e:
        print(f"\n저장 후 데이터 확인 중 오류: {e}")
        sys.stdout.flush()


if __name__ == "__main__":
    collect_in_batches()



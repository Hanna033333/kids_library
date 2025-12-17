import csv
import os
from supabase_client import supabase

def update_from_csv():
    filename = "duplicates_for_manual_check.csv"
    if not os.path.exists(filename):
        print(f"❌ '{filename}' 파일이 없습니다.")
        return

    print("🔄 CSV 파일 읽는 중...")
    
    rows = []
    # 인코딩 시도 (엑셀 저장 시 cp949 가능성)
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    
    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            print(f"✅ 인코딩 감지: {enc}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️ 읽기 오류 ({enc}): {e}")
    
    if not rows:
        print("❌ CSV 파일을 읽을 수 없습니다.")
        return
        
    print(f"📊 총 {len(rows)}개의 데이터를 확인합니다.")
    
    success_count = 0
    updated_items = 0
    
    for row in rows:
        db_id = row.get("DB_ID")
        if not db_id:
            continue
            
        update_data = {}
        
        # 1. 청구기호 업데이트 (사용자가 수정했을 수 있음)
        callno = row.get("청구기호")
        if callno and callno.strip():
            update_data["pangyo_callno"] = callno.strip()
            
        # 2. 권차정보 업데이트 (값이 있는 경우만)
        vol = row.get("권차(입력필요)")
        if vol and vol.strip():
            update_data["vol"] = vol.strip()
            
        if update_data:
            try:
                supabase.table("childbook_items").update(update_data).eq("id", db_id).execute()
                print(f"  ✅ ID {db_id} 업데이트: {update_data}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ ID {db_id} 업데이트 실패: {e}")
        else:
            print(f"  Change skipped for ID {db_id} (No data)")

    print(f"\n✅ 작업 완료: {success_count}건 업데이트됨")

if __name__ == "__main__":
    update_from_csv()

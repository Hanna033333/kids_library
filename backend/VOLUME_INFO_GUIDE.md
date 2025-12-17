# 권차정보 추가 작업 가이드

## 현황
- **중복된 청구기호**: 15개
- **중복된 책**: 31권
- **작업 필요**: 이 책들에대해 Data Library API를 통해 권차정보 조회 및 추가

## 작업 순서

### 1단계: 데이터베이스 스키마 업데이트

Supabase SQL Editor에서 다음 마이그레이션을 실행하세요:

```sql
-- migrations/007_add_vol_column.sql
BEGIN;

-- Add vol column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'childbook_items' AND column_name = 'vol'
    ) THEN
        ALTER TABLE childbook_items ADD COLUMN vol TEXT;
        RAISE NOTICE 'Added vol column to childbook_items';
    ELSE
        RAISE NOTICE 'vol column already exists';
    END IF;
END $$;

-- Create index on vol for faster searches
CREATE INDEX IF NOT EXISTS idx_childbook_items_vol ON childbook_items(vol);

COMMIT;
```

### 2단계: 권차정보 추가 스크립트 실행

```bash
cd backend
python add_volume_info.py
```

이 스크립트는:
1. 중복된 청구기호를 가진 책들을 찾습니다
2. Data Library API (`libSrchByBook`)를 사용하여 각 ISBN의 권차정보를 조회합니다
3. `vol` 파라미터에서 권차정보를 가져옵니다
4. `childbook_items` 테이블의 `vol` 컬럼을 업데이트합니다

## 중복된 청구기호 예시

### 아 813.8-ㄱ985ㄴ (3권)
- 문제아 [ISBN: 9791185934945]
- 문제아 [ISBN: 9788936441753]
- (1권 더)

### 아 808.9-ㅂ854ㅁ (2권)
- 별별수사대 [ISBN: 9791141611422]
- (다른 책)

총 15개의 중복 청구기호에 대해 처리할 예정입니다.

## API 정보

- **API 엔드포인트**: `http://data4library.kr/api/libSrchByBook`
- **권차정보 필드**: `vol`
- **도서관 코드**: `141231` (판교)

## 참고 파일

- `check_duplicate_callnos.py`: 중복 청구기호 분석 스크립트
- `add_volume_info.py`: 권차정보 추가 메인 스크립트
- `migrations/007_add_vol_column.sql`: 스키마 마이그레이션

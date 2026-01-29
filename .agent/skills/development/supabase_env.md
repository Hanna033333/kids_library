## Supabase 환경변수 가이드

### 환경변수 파일 위치
| 용도 | 파일 위치 | 키 종류 |
|------|----------|--------|
| **Frontend** | `frontend/.env.local` | `NEXT_PUBLIC_SUPABASE_ANON_KEY` (읽기 전용) |
| **Backend** | `backend/.env` | `SUPABASE_SERVICE_ROLE_KEY` (읽기/쓰기) |

### Service Role Key 사용 시 주의사항
> [!CAUTION]
> Service Role Key는 **RLS(Row Level Security)를 우회**하므로 절대 클라이언트에 노출하지 마세요.

**Python 스크립트에서 DB 업데이트 시:**
```python
import os
from supabase import create_client
from dotenv import load_dotenv

# backend/.env 사용 (service role key 포함)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")  # 쓰기 권한 필요 시
supabase = create_client(url, key)
```

**사용 케이스:**
- ✅ 일괄 데이터 업데이트 (예: `is_hidden` 처리)
- ✅ 관리자 전용 스크립트
- ❌ 프론트엔드 코드 (절대 사용 금지)
"""
FastAPI 핵심 비즈니스 경로(검색, 인증, 스레드 보안) 단위 및 통합 테스트 코드
"""
import os
import sys
from fastapi.testclient import TestClient

# sys.path 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from api.threads import sign_action, verify_action_signature

client = TestClient(app)

# ============================================
# 1. 책 검색 및 조회 API 테스트
# ============================================

def test_search_books_basic():
    """기본 도서 검색 기능이 작동하는지 테스트"""
    response = client.get("/api/books/search?q=그림책&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert len(data["data"]) <= 5

def test_search_books_escape():
    """검색어 내에 쉼표(,) 및 큰따옴표(")가 섞였을 때 이스케이프가 깨지지 않고 성공하는지 검증 (PostgREST 파서 가용성 테스트)"""
    response = client.get('/api/books/search?q=그림책,"엄마"&limit=1')
    assert response.status_code == 200
    # 파서 에러 422 또는 500이 나지 않고 정상 반환되어야 함
    data = response.json()
    assert "data" in data

# ============================================
# 2. QA 테스터 백도어 토큰 인증 테스트
# ============================================

def test_qa_token_blocked_in_production():
    """ENV == production 일 때는 TEST_QA_TOKEN 백도어가 차단되는지 강제 검증"""
    # 1. ENV=production 환경 시뮬레이션
    os.environ["ENV"] = "production"
    os.environ["ALLOW_QA_MOCK"] = "false"
    
    # 찜 목록 조회 시도 (QA 백도어 토큰 전달)
    response = client.get(
        "/api/wishlists",
        headers={"Authorization": "Bearer TEST_QA_TOKEN"}
    )
    # RLS/인증에 의해 거부되어 401 Unauthorized가 리턴되어야 함 (200 OK 통과 시 백도어 노출 오류)
    assert response.status_code == 401
    assert "사용자 인증에 실패했습니다." in response.json()["detail"]

def test_qa_token_allowed_in_development():
    """ENV == development 일 때는 TEST_QA_TOKEN 백도어가 열리는지 검증"""
    os.environ["ENV"] = "development"
    os.environ["ALLOW_QA_MOCK"] = "true"
    
    response = client.get(
        "/api/wishlists",
        headers={"Authorization": "Bearer TEST_QA_TOKEN"}
    )
    # 개발 모드이므로 200 OK와 모크 데이터를 정상 응답해야 함
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["total"] == 0

# ============================================
# 3. HMAC 기반 스레드 승인 로직 테스트
# ============================================

def test_hmac_signature_generation_and_validation():
    """HMAC SHA-256 서명 생성 및 검증 로직이 정확하게 동작하는지 테스트"""
    os.environ["THREADS_ADMIN_TOKEN"] = "test-admin-secret-token-key-1234"
    
    feed_id = 99
    # 1. 서명값 생성
    sig_text = sign_action("approve-text", feed_id)
    sig_final = sign_action("approve", feed_id)
    
    # 2. 올바른 서명 검증 성공 여부 확인
    assert verify_action_signature("approve-text", feed_id, sig_text) is True
    assert verify_action_signature("approve", feed_id, sig_final) is True
    
    # 3. 잘못된 액션이나 피드 ID를 변조했을 때 차단되는지 검증 (위조 공격 검사)
    assert verify_action_signature("approve", feed_id, sig_text) is False
    assert verify_action_signature("approve-text", 100, sig_text) is False
    assert verify_action_signature("approve-text", feed_id, "invalid-hack-signature") is False

def test_threads_approve_post_validation():
    """승인 POST API submit 호출 시 올바르지 않은 서명이 유입되었을 때 401 차단되는지 테스트"""
    os.environ["THREADS_ADMIN_TOKEN"] = "test-admin-secret-token-key-1234"
    
    # 위조 서명으로 포스트 요청 발송
    response = client.post(
        "/api/threads/approve-text/submit",
        json={"feed_id": 99, "signature": "forged-signature-value"}
    )
    assert response.status_code == 401
    assert "유효하지 않은 관리자 서명입니다." in response.json()["detail"]

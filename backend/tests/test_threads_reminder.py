"""
오후 6시 스레드 미승인 리마인더(send_unapproved_threads_reminder) 단위 테스트
"""
import asyncio
import datetime
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api.threads as threads_module


def _make_supabase_mock(query_results):
    """supabase.table('threads_feeds').select(...) 체인 호출 결과를 순서대로 반환하는 모크 생성"""
    results_iter = iter(query_results)

    def _make_chain():
        chain = MagicMock()
        for method in ("select", "eq", "is_", "gte", "order", "limit"):
            getattr(chain, method).return_value = chain

        def _execute():
            res = MagicMock()
            res.data = next(results_iter)
            return res

        chain.execute.side_effect = _execute
        return chain

    sb = MagicMock()
    sb.table.side_effect = lambda _name: _make_chain()
    return sb


def test_reminder_skipped_when_approved_today():
    """오늘자 피드가 이미 승인 완료된 경우 텔레그램 리마인더를 발송하지 않아야 함"""
    sb_mock = _make_supabase_mock([
        [{"id": 101}],  # approved_today
    ])
    send_mock = AsyncMock(return_value=True)

    with patch.object(threads_module, "supabase", sb_mock), \
         patch.object(threads_module, "send_telegram_message", send_mock):
        sent = asyncio.run(threads_module.send_unapproved_threads_reminder(datetime.date(2026, 11, 23)))

    assert sent is False
    send_mock.assert_not_called()


def test_reminder_sent_for_stage1_pending_feed():
    """1단계 텍스트 승인 대기(image_urls 없음) 시 approve-text 버튼과 함께 리마인더 발송"""
    sb_mock = _make_supabase_mock([
        [],  # approved_today
        [{"id": 202, "title": "스르륵 꿀잠 그림책", "curation_tag": "잠자리", "image_urls": None}],  # pending_today
    ])
    send_mock = AsyncMock(return_value=True)

    with patch.object(threads_module, "supabase", sb_mock), \
         patch.object(threads_module, "send_telegram_message", send_mock), \
         patch.object(threads_module, "THREADS_ADMIN_TOKEN", "test-secret-token"):
        sent = asyncio.run(threads_module.send_unapproved_threads_reminder(datetime.date(2026, 11, 23)))

    assert sent is True
    send_mock.assert_awaited_once()
    args, kwargs = send_mock.call_args
    assert "1단계 텍스트 승인" in args[0]
    assert "스르륵 꿀잠 그림책" in args[0]
    assert kwargs["button_text"] == "🎨 카드뉴스 이미지 생성 및 2차 검증하기"
    assert "/api/threads/approve-text?" in kwargs["button_url"]
    assert "feed_id=202" in kwargs["button_url"]


def test_reminder_sent_for_stage2_pending_feed():
    """2단계 최종 승인 대기(image_urls 존재) 시 approve 버튼과 함께 리마인더 발송"""
    sb_mock = _make_supabase_mock([
        [],  # approved_today
        [{"id": 303, "title": "우리 아이 감정 수업", "curation_tag": "감정조절", "image_urls": ["https://a", "https://b"]}],
    ])
    send_mock = AsyncMock(return_value=True)

    with patch.object(threads_module, "supabase", sb_mock), \
         patch.object(threads_module, "send_telegram_message", send_mock), \
         patch.object(threads_module, "THREADS_ADMIN_TOKEN", "test-secret-token"):
        sent = asyncio.run(threads_module.send_unapproved_threads_reminder(datetime.date(2026, 11, 23)))

    assert sent is True
    send_mock.assert_awaited_once()
    args, kwargs = send_mock.call_args
    assert "최종 발행 승인" in args[0]
    assert "2장" in args[0]
    assert kwargs["button_text"] == "✅ 발행 승인 완료하기"
    assert "/api/threads/approve?" in kwargs["button_url"]
    assert "feed_id=303" in kwargs["button_url"]


def test_reminder_skipped_when_recent_approved_unpublished_exists():
    """오늘자 피드는 없지만 최근 7일 내 승인 완료 미발행 건이 있으면 리마인더 생략"""
    sb_mock = _make_supabase_mock([
        [],  # approved_today
        [],  # pending_today
        [{"id": 404}],  # approved_recent
    ])
    send_mock = AsyncMock(return_value=True)

    with patch.object(threads_module, "supabase", sb_mock), \
         patch.object(threads_module, "send_telegram_message", send_mock):
        sent = asyncio.run(threads_module.send_unapproved_threads_reminder(datetime.date(2026, 11, 23)))

    assert sent is False
    send_mock.assert_not_called()


def test_reminder_sent_when_no_feed_exists_today():
    """오늘자 피드도 없고 최근 승인 예약 건도 없으면 안내 리마인더 발송"""
    sb_mock = _make_supabase_mock([
        [],  # approved_today
        [],  # pending_today
        [],  # approved_recent
    ])
    send_mock = AsyncMock(return_value=True)

    with patch.object(threads_module, "supabase", sb_mock), \
         patch.object(threads_module, "send_telegram_message", send_mock):
        sent = asyncio.run(threads_module.send_unapproved_threads_reminder(datetime.date(2026, 11, 23)))

    assert sent is True
    send_mock.assert_awaited_once()
    args, kwargs = send_mock.call_args
    assert "생성되거나 승인된 스레드 시안이 없습니다" in args[0]
    assert kwargs == {}

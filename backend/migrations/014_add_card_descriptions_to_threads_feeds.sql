-- 1. card_descriptions 컬럼 추가 (각 카드뉴스에 박아 넣을 AI 생성 요약 텍스트 임시 보관용)
ALTER TABLE public.threads_feeds ADD COLUMN IF NOT EXISTS card_descriptions TEXT[];

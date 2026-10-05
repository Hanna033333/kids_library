-- ============================================
-- 025_fix_security_advisor_warnings.sql
-- 목적: Supabase Security Advisor 경고 6건 일괄 해결
--   1. Function Search Path Mutable 보안 취약점 해결 (search_path 명시)
--   2. SECURITY DEFINER 함수(handle_new_user) 직접 실행 권한 제한
-- ============================================

-- 1. generate_random_nickname search_path 고정
CREATE OR REPLACE FUNCTION public.generate_random_nickname()
RETURNS TEXT 
LANGUAGE plpgsql 
VOLATILE
SET search_path = public, pg_temp
AS $$
DECLARE
  adjectives TEXT[] := ARRAY[
    '지혜로운', '따스한', '포근한', '정겨운', '행복한', '다정한', '꿈꾸는', '다독이는', '슬기로운', '다복한', 
    '마음넓은', '빛나는', '즐거운', '상냥한', '반짝이는', '용감한', '푸른', '희망찬', '해맑은', '고마운', 
    '포근포근', '싱그러운', '너그러운', '새싹같은', '옹달샘', '보드라운', '초롱초롱', '알록달록', '은은한', '산뜻한',
    '사랑스런', '명랑한', '슬기찬', '어질고', '호기심찬', '눈부신', '도란도란', '달콤한', '미소짓는', '소담한',
    '재치있는', '기운찬', '활기찬', '따사로운', '아늑한', '별처럼', '구름같은', '무지개빛', '정다운', '온화한',
    '단단한', '자유로운', '맑고밝은', '조잘조잘', '살가운', '도란대는', '생글생글', '두근두근', '소복소복', '풍성한',
    '향기로운', '든든한', '기쁨가득', '마음고운', '생각깊은', '지혜가득', '꿈이많은', '찬란한', '싱글벙글', '방긋웃는',
    '풋풋한', '순수한', '맑은눈의', '꿈꾸듯', '솔솔부는', '똘똘한', '야무진', '의젓한', '씩씩한', '반듯한'
  ];
  nouns TEXT[] := ARRAY[
    '책벌레', '이야기꾼', '책부엉이', '파랑새', '독서가', '책요정', '글벗', '책탐험가', '책마을님', '도토리',
    '꿈나무', '독서왕', '별나무', '책친구', '아기도깨비', '책다람쥐', '토끼', '작은새', '어린사자', '꼬마곰',
    '책박사', '길잡이', '책마법사', '글마루', '책지기', '동화작가', '숲속요정', '별똥별', '새싹', '햇살이',
    '달팽이', '꽃사슴', '아기호랑이', '책누리', '글꽃', '책별', '은하수', '숲속친구', '이야기샘', '책방주인',
    '글타래', '책등대', '지혜샘', '달맞이', '별지기', '숲지기', '꿈꾸미', '도서관지기', '글동무', '책풍경',
    '호기심대장', '상상왕', '생각나무', '독서대장', '마음상자', '이야기별', '책바다', '단풍잎', '은행잎', '솔방울',
    '아기참새', '책정원', '글나라', '동화나무', '책소리', '글소리', '달빛요정', '별빛마을', '작은여우', '아기달님',
    '숲속곰돌이', '꼬마별', '책마중', '글나래', '꿈나래', '새싹지기', '솔바람', '들꽃', '책보따리', '이야기꽃'
  ];
  adj_len INT := array_length(adjectives, 1);
  noun_len INT := array_length(nouns, 1);
  rand_num INT := floor(100 + random() * 900)::int;
BEGIN
  RETURN adjectives[1 + floor(random() * adj_len)::int] || nouns[1 + floor(random() * noun_len)::int] || rand_num::text;
END;
$$;

-- 2. handle_new_user search_path 고정 및 권한 제한
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER 
LANGUAGE plpgsql 
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  generated_nick TEXT;
BEGIN
  generated_nick := public.generate_random_nickname();

  INSERT INTO public.members (
    id,
    email,
    provider,
    provider_id,
    nickname,
    agreed_to_terms,
    agreed_to_privacy,
    agreed_to_marketing
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
    COALESCE(NEW.raw_user_meta_data->>'provider_id', NEW.id::text),
    generated_nick,
    true,
    true,
    false
  )
  ON CONFLICT (id) DO UPDATE
  SET nickname = COALESCE(public.members.nickname, EXCLUDED.nickname);

  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;
END;
$$;

-- 일반 유저/익명 유저의 직접 실행 권한 회수 (트리거로만 실행되도록 보호)
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM anon, authenticated;

-- 3. update_updated_at_column search_path 고정
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER 
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

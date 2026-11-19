-- ============================================
-- 026_unique_nickname.sql
-- 목적:
--   1. members 테이블의 nickname 중복 방지 (UNIQUE 인덱스)
--   2. 실시간 닉네임 중복 검사용 RPC 함수(is_nickname_available) 생성
--   3. 자동 생성 닉네임에서 숫자 제거 및 중복 회피 루프 적용
-- ============================================

-- 1. members 테이블 nickname 컬럼에 UNIQUE 인덱스 생성 (NULL 제외)
CREATE UNIQUE INDEX IF NOT EXISTS uix_members_nickname ON public.members (nickname) WHERE nickname IS NOT NULL;

-- 2. 닉네임 중복 검사용 RPC 함수 (RLS 제약 없이 프론트엔드/백엔드에서 안전하게 호출 가능)
CREATE OR REPLACE FUNCTION public.is_nickname_available(p_nickname TEXT, p_user_id UUID DEFAULT NULL)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_clean TEXT := trim(p_nickname);
  v_exists BOOLEAN;
BEGIN
  -- 유효성 검사 (2~10자, 공백 불가)
  IF length(v_clean) < 2 OR length(v_clean) > 10 OR v_clean ~ '\s' THEN
    RETURN FALSE;
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM public.members
    WHERE nickname = v_clean
      AND (p_user_id IS NULL OR id != p_user_id)
  ) INTO v_exists;

  RETURN NOT v_exists;
END;
$$;

-- 익명 유저(가입 전) 및 로그인 유저 모두에게 함수 실행 권한 부여
GRANT EXECUTE ON FUNCTION public.is_nickname_available(TEXT, UUID) TO anon, authenticated, service_role;

-- 3. 자동 닉네임 생성 함수: 숫자 제거 및 중복 회피 루프(최대 20회) 적용
CREATE OR REPLACE FUNCTION public.generate_random_nickname()
RETURNS TEXT 
LANGUAGE plpgsql 
SECURITY DEFINER
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
  candidate TEXT;
  tries INT := 0;
  is_dup BOOLEAN;
BEGIN
  -- 형용사(80) x 명사(80) = 6,400개 조합 중 중복되지 않는 닉네임 탐색
  LOOP
    tries := tries + 1;
    candidate := adjectives[1 + floor(random() * adj_len)::int] || nouns[1 + floor(random() * noun_len)::int];
    
    SELECT EXISTS(SELECT 1 FROM public.members WHERE nickname = candidate) INTO is_dup;
    IF NOT is_dup THEN
      RETURN candidate;
    END IF;

    -- 20회 연속 충돌 시 예외적 안전장치로 난수 2자리 덧붙여 UNIQUE 충돌 방지
    IF tries >= 20 THEN
      RETURN candidate || floor(10 + random() * 90)::int::text;
    END IF;
  END LOOP;
END;
$$;

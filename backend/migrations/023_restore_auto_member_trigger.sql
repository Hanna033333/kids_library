-- ============================================
-- 023_restore_auto_member_trigger.sql
-- 목적: auth.users → members 동기화를 DB 트리거로 복원
--
-- 배경:
--   010에서 도입한 on_auth_user_created 트리거를 018에서 제거했다.
--   제거 사유는 "약관 미동의 회원 자동 저장 방지"였다. 당시 트리거는
--   agreed_to_terms/agreed_to_privacy를 지정하지 않아 DEFAULT false로
--   들어갔고, 그 결과 동의하지 않은 사람의 레코드가 쌓였기 때문이다.
--
--   018 이후 members 생성은 브라우저 → 백엔드 API(/api/auth/me/agreements)
--   왕복에 의존하게 됐고, 이 구간이 끊기면 가입이 통째로 유실된다.
--   실제로 2026-08-27 카카오 인증까지 마친 사용자가 members에 남지 않았다.
--
--   2026-08-28(9bb2b53)에 약관 동의 화면을 제거하고 "로그인하면 약관에
--   동의한 것으로 간주"하는 UX로 전환하면서, 018의 전제인 '약관 미동의 회원'
--   개념 자체가 사라졌다. 따라서 트리거를 복원하되 018이 겪은 문제를
--   반복하지 않도록 동의 컬럼을 명시적으로 true로 지정한다.
--
-- 성격:
--   저장되는 값과 위치는 기존 백엔드 API와 동일하다(members.agreed_to_terms
--   = true). 쓰기 주체만 네트워크 왕복에서 DB 내부로 옮겨 유실 구간을 없앤다.
--   백엔드 API는 닉네임 등 프로필 갱신 역할로 계속 사용된다(upsert).
-- ============================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.members (
    id,
    email,
    provider,
    provider_id,
    agreed_to_terms,
    agreed_to_privacy,
    agreed_to_marketing
  )
  VALUES (
    NEW.id,
    -- 이메일은 지어내지 않는다. members.email이 NOT NULL이므로 이메일 없이는
    -- 회원 레코드를 만들 수 없고, 그 경우 INSERT가 실패해 아래 EXCEPTION이
    -- 삼킨다(= members 행 미생성 = 가입 미완료).
    --
    -- 카카오는 account_email을, 구글은 email scope를 각각 필수로 요구하도록
    -- 설정돼 있어 실제로는 NULL이 오지 않는다. 이 전제가 깨지면(동의항목을
    -- 선택으로 되돌리는 등) 인증은 됐는데 members가 없는 계정이 생길 수 있으므로,
    -- 동의항목을 변경할 때는 이 제약을 함께 검토해야 한다.
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
    COALESCE(NEW.raw_user_meta_data->>'provider_id', NEW.id::text),
    -- 로그인 시점이 곧 동의 시점이다 (AuthClient.tsx 하단 고지 문구와 일치)
    true,
    true,
    -- 마케팅 수신은 별도 선택 동의 대상이므로 false를 유지한다
    false
  )
  ON CONFLICT (id) DO NOTHING;

  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    -- 트리거 실패가 인증 자체를 막아서는 안 된다.
    -- 실패하더라도 콜백의 등록 API 재시도가 2차 방어선으로 남는다.
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- 검증 쿼리 (적용 후 수동 실행)
--
--   -- 트리거 등록 확인 (1행 나와야 정상)
--   SELECT tgname FROM pg_trigger WHERE tgname = 'on_auth_user_created';
--
--   -- 고아 계정 확인 (0행이어야 정상)
--   SELECT u.id, u.email, u.created_at
--   FROM auth.users u
--   LEFT JOIN public.members m ON m.id = u.id
--   WHERE m.id IS NULL;
-- ============================================

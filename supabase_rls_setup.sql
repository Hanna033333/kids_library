-- ============================================
-- Supabase RLS 보안 설정 (필수!)
-- ============================================
-- 이 SQL을 Supabase Dashboard → SQL Editor에서 실행하세요.

-- 1. RLS 활성화
ALTER TABLE childbook_items ENABLE ROW LEVEL SECURITY;

-- 2. 읽기 전용 정책 (anon 사용자가 SELECT만 가능)
CREATE POLICY "Public read access"
ON childbook_items
FOR SELECT
TO anon
USING (true);

-- 3. 쓰기 완전 차단 (INSERT, UPDATE, DELETE 모두 차단)
CREATE POLICY "No public insert"
ON childbook_items
FOR INSERT
TO anon
WITH CHECK (false);

CREATE POLICY "No public update"
ON childbook_items
FOR UPDATE
TO anon
USING (false);

CREATE POLICY "No public delete"
ON childbook_items
FOR DELETE
TO anon
USING (false);

-- ============================================
-- 보안 테스트 (브라우저 콘솔에서 실행)
-- ============================================
-- 아래 코드를 브라우저 개발자 도구 콘솔에서 실행하여 보안 확인

/*
// 1. 읽기 테스트 (성공해야 함)
const { data, error } = await supabase
  .from('childbook_items')
  .select('*')
  .limit(1);
console.log('Read test:', data ? '✅ Success' : '❌ Failed', error);

// 2. 쓰기 테스트 (실패해야 함)
const { error: insertError } = await supabase
  .from('childbook_items')
  .insert({ title: 'hack' });
console.log('Insert test:', insertError ? '✅ Blocked (Good!)' : '❌ Not blocked (Bad!)');

// 3. 수정 테스트 (실패해야 함)
const { error: updateError } = await supabase
  .from('childbook_items')
  .update({ title: 'hacked' })
  .eq('id', 1);
console.log('Update test:', updateError ? '✅ Blocked (Good!)' : '❌ Not blocked (Bad!)');

// 4. 삭제 테스트 (실패해야 함)
const { error: deleteError } = await supabase
  .from('childbook_items')
  .delete()
  .eq('id', 1);
console.log('Delete test:', deleteError ? '✅ Blocked (Good!)' : '❌ Not blocked (Bad!)');
*/

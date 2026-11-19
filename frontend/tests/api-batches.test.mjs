import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchLoanStatuses, getBooksByIds } from '../lib/api';

afterEach(() => vi.unstubAllGlobals());

describe('도서 일괄 조회', () => {
  it.each([0, 1, 50, 51, 72, 201])('%i권을 누락 없이 조회하고 최대 3개 요청만 동시에 실행한다', async (count) => {
    const ids = Array.from({ length: count }, (_, i) => i + 1);
    let active = 0;
    let peak = 0;
    const requested = [];
    const fetch = vi.fn(async (_url, options) => {
      const batch = JSON.parse(options.body);
      requested.push(...batch);
      expect(batch.length).toBeLessThanOrEqual(50);
      peak = Math.max(peak, ++active);
      await new Promise(resolve => setTimeout(resolve, 2));
      active--;
      // 서버 응답 순서와 무관하게 입력 순서를 복원해야 한다.
      return Response.json(batch.toReversed().map(id => ({ id })));
    });
    vi.stubGlobal('fetch', fetch);
    const books = await getBooksByIds([...ids, ...ids.slice(0, 3)]);
    expect(books.map(book => book.id)).toEqual(ids);
    expect(requested).toEqual(ids);
    expect(fetch).toHaveBeenCalledTimes(Math.ceil(count / 50));
    expect(peak).toBeLessThanOrEqual(3);
  });

  it('대출 상태는 중복 ID를 제거하고 모든 배치 결과를 같은 도서관으로 병합한다', async () => {
    const ids = Array.from({ length: 72 }, (_, i) => i + 1);
    const fetch = vi.fn(async (_url, options) => {
      const { book_ids, library_name } = JSON.parse(options.body);
      expect(library_name).toBe('송파어린이도서관');
      expect(book_ids.length).toBeLessThanOrEqual(50);
      return Response.json(Object.fromEntries(book_ids.map(id => [id, { available: true, status: '대출가능' }])));
    });
    vi.stubGlobal('fetch', fetch);
    const result = await fetchLoanStatuses([...ids, 1], '송파어린이도서관');
    expect(Object.keys(result)).toHaveLength(72);
    expect(result[72].available).toBe(true);
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('빈 대출 요청은 네트워크를 호출하지 않는다', async () => {
    const fetch = vi.fn();
    vi.stubGlobal('fetch', fetch);
    expect(await fetchLoanStatuses([])).toEqual({});
    expect(fetch).not.toHaveBeenCalled();
  });

  it('일부 배치 실패를 성공한 전체 조회로 숨기지 않는다', async () => {
    vi.stubGlobal('fetch', vi.fn(async (_url, options) => {
      const batch = JSON.parse(options.body);
      return batch[0] === 51 ? new Response(null, { status: 500 }) : Response.json(batch.map(id => ({ id })));
    }));
    await expect(getBooksByIds(Array.from({ length: 51 }, (_, i) => i + 1))).rejects.toThrow();
  });
});

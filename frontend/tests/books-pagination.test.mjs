import { afterEach, expect, it, vi } from 'vitest';
import { InfiniteQueryObserver, QueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { useBooks } from '../hooks/useBooks';
import { searchBooks } from '../lib/api';

vi.mock('@tanstack/react-query', async importOriginal => ({
  ...await importOriginal(),
  useInfiniteQuery: vi.fn(() => ({ data: undefined, isLoading: false })),
}));
vi.mock('../lib/api', () => ({ searchBooks: vi.fn() }));
afterEach(() => vi.clearAllMocks());

const firstPage = {
  data: Array.from({ length: 24 }, (_, i) => ({ id: i + 1 })),
  total: 51, total_pages: 3, page: 1, limit: 24,
};

function optionsFor(params) {
  useBooks(params);
  return vi.mocked(useInfiniteQuery).mock.calls.at(-1)[0];
}

it('서버 초기 페이지의 전체 건수를 보존하고 즉시 다음 페이지를 조회한다', async () => {
  const options = optionsFor({ initialPage: firstPage });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
  const observer = new InfiniteQueryObserver(client, options);
  try {
    expect(observer.getCurrentResult().data.pages[0]).toEqual(firstPage);
    expect(observer.getCurrentResult().hasNextPage).toBe(true);
    vi.mocked(searchBooks).mockResolvedValueOnce({ ...firstPage, data: [{ id: 25 }], page: 2 });
    await observer.fetchNextPage();
    expect(searchBooks.mock.calls[0][4]).toBe(2);
    expect(observer.getCurrentResult().data.pages).toHaveLength(2);
  } finally {
    observer.destroy();
    client.clear();
  }
});

it('마지막 페이지 뒤에는 다음 페이지를 만들지 않는다', () => {
  const options = optionsFor({});
  expect(options.getNextPageParam({ ...firstPage, page: 3 })).toBeUndefined();
});

it('페이지 크기와 정렬이 다르면 캐시를 분리한다', () => {
  const base = optionsFor({ limit: 24, sortFilter: 'title' });
  expect(optionsFor({ limit: 50, sortFilter: 'title' }).queryKey).not.toEqual(base.queryKey);
  expect(optionsFor({ limit: 24, sortFilter: 'popular' }).queryKey).not.toEqual(base.queryKey);
});

it('페이지 크기 또는 도서관 데이터 요구 조건이 다르면 초기 데이터를 재사용하지 않는다', () => {
  expect(optionsFor({ initialPage: firstPage, limit: 50 }).initialData).toBeUndefined();
  expect(optionsFor({ initialPage: firstPage, includeLibraryInfo: true }).initialData).toBeUndefined();
  const withLibraries = { ...firstPage, data: firstPage.data.map(book => ({ ...book, library_info: [] })) };
  expect(optionsFor({ initialPage: withLibraries, includeLibraryInfo: true }).initialData.pages[0]).toEqual(withLibraries);
});

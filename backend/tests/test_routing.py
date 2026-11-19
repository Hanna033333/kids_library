"""외부 DB 접근 없이 정적/동적 도서 경로의 우선순위를 검증한다."""
import unittest

from fastapi.testclient import TestClient
from starlette.routing import Match
from main import app


class BookRoutingTests(unittest.TestCase):
    def test_book_route_targets(self):
        for path, endpoint in [
            ("/api/books/my-reviews", "get_my_reviews"),
            ("/api/books/search", "search_books"),
            ("/api/books/1", "get_book_detail"),
            ("/api/books/1/reviews", "get_book_reviews"),
        ]:
            with self.subTest(path=path):
                scope = {"type": "http", "method": "GET", "path": path, "root_path": ""}
                first = next(route for route in app.routes if route.matches(scope)[0] == Match.FULL)
                self.assertEqual(first.endpoint.__name__, endpoint)

    def test_my_reviews_requires_auth_instead_of_parsing_book_id(self):
        # context manager를 사용하지 않아 발행 스케줄러/lifespan은 실행하지 않는다.
        response = TestClient(app).get("/api/books/my-reviews")
        self.assertIn(response.status_code, (401, 403))


if __name__ == "__main__":
    unittest.main()

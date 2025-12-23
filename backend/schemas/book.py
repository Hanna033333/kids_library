"""책 데이터 모델"""
from pydantic import BaseModel
from typing import Optional


class BookSearchParams(BaseModel):
    """책 검색 파라미터"""
    q: Optional[str] = None
    age: Optional[str] = None
    sort: str = "pangyo_callno"
    page: int = 1
    limit: int = 20


class BookResponse(BaseModel):
    """책 응답 데이터"""
    id: Optional[int] = None
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    pangyo_callno: Optional[str] = None
    age: Optional[str] = None


class BooksListResponse(BaseModel):
    """책 목록 응답 데이터"""
    data: list[BookResponse]
    total: int
    page: int
    limit: int
    total_pages: int







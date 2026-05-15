"""
Pagination utilities for standardizing list endpoints.
"""
from typing import Generic, List, Optional, TypeVar, Dict, Any
from fastapi import Query
from pydantic import BaseModel
import math

T = TypeVar("T")

class PageParams:
    """
    Standard pagination parameters.
    Accepts `page` and `limit` query parameters. Defaults: `page=1`, `limit=50`.
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number starting from 1"),
        limit: int = Query(50, ge=1, le=500, description="Number of items per page (max 500)"),
        page_size: Optional[int] = Query(None, alias="page_size", description="Legacy page_size (if provided, overrides limit)")
    ):
        self.page = page
        # Accept legacy `page_size` query param if provided
        self.limit = page_size if page_size is not None else limit
        self.skip = (page - 1) * self.limit


class Page(BaseModel, Generic[T]):
    """
    Standard pagination response that includes metadata.
    Fields: items, total, page, limit, total_pages
    """
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PageParams) -> "Page[T]":
        """Create a Page from a list of items, total count, and page parameters."""
        total_pages = math.ceil(total / params.limit) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            total_pages=total_pages,
        )


def paginate_query(query: Any, params: PageParams) -> Dict[str, Any]:
    """
    Apply pagination to a SQLAlchemy query and return a dict with items and total.
    This helper uses `limit` from PageParams.
    """
    total = query.count()
    items = query.offset(params.skip).limit(params.limit).all()
    return {
        "items": items,
        "total": total,
    }
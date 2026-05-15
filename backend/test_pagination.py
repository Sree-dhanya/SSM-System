"""Basic tests for students pagination endpoint.

These tests expect the backend to be running locally at http://localhost:8000.
They are intentionally lightweight and focus only on pagination metadata
and behavior when requesting a page beyond the available range.
"""
import math
import pytest
import requests

BASE = "http://localhost:8000"
URL = f"{BASE}/api/v1/students/"


def test_pagination_metadata():
    params = {"page": 1, "limit": 5}
    r = requests.get(URL, params=params)
    assert r.status_code == 200, "Backend must be running at http://localhost:8000"
    data = r.json()
    assert isinstance(data, dict)
    for key in ("items", "total", "page", "limit", "total_pages"):
        assert key in data, f"Missing key {key} in response"

    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert data["page"] == 1
    assert data["limit"] == 5
    assert isinstance(data["total_pages"], int)


def test_page_beyond_returns_empty_or_zero_total():
    # Determine total using limit=1 so total_pages == total
    r = requests.get(URL, params={"page": 1, "limit": 1})
    assert r.status_code == 200, "Backend must be running at http://localhost:8000"
    data = r.json()
    total = data.get("total", 0)

    if total == 0:
        pytest.skip("No students in database to test page-beyond behavior")

    beyond_page = total + 1
    r2 = requests.get(URL, params={"page": beyond_page, "limit": 1})
    assert r2.status_code == 200
    d2 = r2.json()
    assert isinstance(d2.get("items", None), list)
    assert d2.get("items", []) == []
    assert d2.get("page") == beyond_page

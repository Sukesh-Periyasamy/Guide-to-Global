"""
Search route: GET /search?q=<query>
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from backend.services.search_service import filter_programs, search_programs

router = APIRouter(tags=["search"])


@router.get("/search", summary="Search programs by keyword")
def search(
    q: str = Query(..., description="Keyword to search across university name, program name, and department"),
) -> List[Dict[str, Any]]:
    """
    Search university programs.

    Returns all documents where the query matches (case-insensitive) the
    university name, program name, or department field.
    """
    results = search_programs(q)
    return results


@router.get("/filter", summary="Filter programs by country and/or degree")
def filter_route(
    country: str | None = Query(None, description="Country name (e.g. Germany)"),
    degree: str | None = Query(None, description="Degree type (e.g. Masters, PhD)"),
) -> List[Dict[str, Any]]:
    """
    Filter programs by country and/or degree level.

    At least one query parameter should be provided; if both are omitted the
    full collection is returned.
    """
    return filter_programs(country, degree)

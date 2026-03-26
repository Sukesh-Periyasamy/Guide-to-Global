"""
Program route: GET /program/{id}
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.services.search_service import get_program_by_id

router = APIRouter(tags=["programs"])


@router.get("/program/{program_id}", summary="Get program details by ID")
def get_program(program_id: str) -> Dict[str, Any]:
    """
    Retrieve a full program document by its MongoDB ObjectId.

    Returns 404 if the id is invalid or not found.
    """
    doc = get_program_by_id(program_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return doc

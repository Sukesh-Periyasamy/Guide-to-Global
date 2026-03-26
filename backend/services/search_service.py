"""
Search service: queries MongoDB for programs matching user criteria.
"""

from typing import Any, Dict, List

from bson import ObjectId
from pymongo.collection import Collection

from backend.db.mongo import programs_collection


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ObjectId fields to strings so they can be JSON-serialised."""
    doc["_id"] = str(doc["_id"])
    return doc


def search_programs(query: str) -> List[Dict[str, Any]]:
    """
    Full-text style search across university name, program name, and department.

    Uses case-insensitive regex queries so no full-text index is required.
    """
    regex = {"$regex": query, "$options": "i"}
    cursor = programs_collection.find(
        {
            "$or": [
                {"university.name": regex},
                {"program.name": regex},
                {"program.department": regex},
            ]
        }
    )
    return [_serialize(doc) for doc in cursor]


def filter_programs(country: str | None, degree: str | None) -> List[Dict[str, Any]]:
    """
    Filter programs by country and/or degree.

    Both filters are optional and case-insensitive.
    """
    filters: Dict[str, Any] = {}
    if country:
        filters["university.country"] = {"$regex": country, "$options": "i"}
    if degree:
        filters["program.degree"] = {"$regex": degree, "$options": "i"}

    cursor = programs_collection.find(filters)
    return [_serialize(doc) for doc in cursor]


def get_program_by_id(program_id: str) -> Dict[str, Any] | None:
    """Return a single program document by its MongoDB ObjectId string."""
    try:
        oid = ObjectId(program_id)
    except Exception:
        return None
    doc = programs_collection.find_one({"_id": oid})
    return _serialize(doc) if doc else None

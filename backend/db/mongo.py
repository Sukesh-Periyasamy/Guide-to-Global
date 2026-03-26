"""
MongoDB connection and collection helpers.

Creates a single MongoClient that is reused across the application lifetime.
Indexes are created on startup to support efficient search and filter queries.
"""

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from config.settings import settings

# ---------------------------------------------------------------------------
# Client / database singletons
# ---------------------------------------------------------------------------

_client: MongoClient = MongoClient(settings.MONGO_URI)
_db: Database = _client[settings.DATABASE_NAME]

# Primary collection
programs_collection: Collection = _db["programs"]


def create_indexes() -> None:
    """Create MongoDB indexes required for search and filtering."""
    programs_collection.create_index([("university.name", ASCENDING)], name="idx_university_name")
    programs_collection.create_index([("program.name", ASCENDING)], name="idx_program_name")
    programs_collection.create_index([("admission.deadline", ASCENDING)], name="idx_admission_deadline")

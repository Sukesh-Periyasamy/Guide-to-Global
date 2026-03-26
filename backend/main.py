"""
FastAPI application entry point.

Run with:
    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI

from backend.db.mongo import create_indexes
from backend.routes.program import router as program_router
from backend.routes.search import router as search_router

app = FastAPI(
    title="Guide to Global – University Admission Intelligence API",
    description=(
        "Search and explore global university programs, admission requirements, "
        "deadlines, and eligibility criteria."
    ),
    version="1.0.0",
)

# Register route modules
app.include_router(search_router)
app.include_router(program_router)


@app.on_event("startup")
def startup_event() -> None:
    """Create MongoDB indexes when the server starts."""
    create_indexes()


@app.get("/", tags=["health"])
def root() -> dict:
    """Health-check endpoint."""
    return {"status": "ok", "message": "Guide to Global API is running"}

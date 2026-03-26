"""
Scraper runner: orchestrates fetching, extraction, and storage.

Usage (from project root):
    python -m scraper.runner --url https://example.edu/program

Or seed the database with built-in sample data:
    python -m scraper.runner --seed
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any, Dict

from backend.db.mongo import programs_collection
from scraper.extractor import extract_program_data
from scraper.scrapling_client import fetch_html


# ---------------------------------------------------------------------------
# Sample data (used for local development / testing)
# ---------------------------------------------------------------------------

SAMPLE_PROGRAMS: list[Dict[str, Any]] = [
    {
        "university": {
            "name": "Technical University of Munich",
            "country": "Germany",
            "city": "Munich",
        },
        "program": {
            "name": "M.Sc. Artificial Intelligence",
            "degree": "Masters",
            "department": "Computer Science",
            "duration": "2 years",
        },
        "admission": {
            "status": "open",
            "intake": "Winter 2025",
            "deadline": "2025-05-31",
        },
        "requirements": {
            "ielts": {"required": True, "min_score": 7.0},
            "toefl": {"required": False, "min_score": None},
            "gre": {"required": False, "recommended": True, "min_score": None},
            "documents": {
                "lor": 2,
                "sop": True,
                "resume": True,
                "transcript": True,
            },
        },
        "financial": {
            "tuition_fee": "€0 (state-funded)",
            "scholarship_available": True,
        },
        "links": {
            "admission_page": "https://www.tum.de/en/studies/admission",
            "program_page": "https://www.tum.de/en/studies/degree-programs/detail/artificial-intelligence-msc",
            "apply_link": "https://www.tum.de/en/studies/application",
        },
        "raw_data": {
            "requirements_text": "IELTS 7.0 required. 2 Letters of Recommendation. SOP required.",
            "description_text": "The M.Sc. AI program at TUM focuses on machine learning, robotics, and cognitive systems.",
        },
        "metadata": {
            "last_scraped": datetime.now(timezone.utc).isoformat(),
            "source": "https://www.tum.de",
        },
    },
    {
        "university": {
            "name": "University of Toronto",
            "country": "Canada",
            "city": "Toronto",
        },
        "program": {
            "name": "Master of Engineering in Machine Learning",
            "degree": "Masters",
            "department": "Electrical and Computer Engineering",
            "duration": "1 year",
        },
        "admission": {
            "status": "open",
            "intake": "Fall 2025",
            "deadline": "2025-02-01",
        },
        "requirements": {
            "ielts": {"required": True, "min_score": 6.5},
            "toefl": {"required": True, "min_score": 93},
            "gre": {"required": False, "recommended": False, "min_score": None},
            "documents": {
                "lor": 3,
                "sop": True,
                "resume": True,
                "transcript": True,
            },
        },
        "financial": {
            "tuition_fee": "CAD $28,000/year",
            "scholarship_available": True,
        },
        "links": {
            "admission_page": "https://www.engineering.utoronto.ca/graduate/admissions/",
            "program_page": "https://www.ece.utoronto.ca/graduate/meng-machine-learning/",
            "apply_link": "https://apply.engineering.utoronto.ca/",
        },
        "raw_data": {
            "requirements_text": (
                "IELTS 6.5 or TOEFL 93 required. 3 Letters of Recommendation. "
                "Statement of Purpose, resume, and official transcripts required."
            ),
            "description_text": (
                "A one-year professional program covering deep learning, computer vision, "
                "and natural language processing."
            ),
        },
        "metadata": {
            "last_scraped": datetime.now(timezone.utc).isoformat(),
            "source": "https://www.utoronto.ca",
        },
    },
]


# ---------------------------------------------------------------------------
# Core scrape function
# ---------------------------------------------------------------------------


def scrape(url: str) -> Dict[str, Any]:
    """
    Fetch *url*, extract structured program data, and return the dict.

    Note: The caller is responsible for filling in university / program meta
    fields that cannot be reliably extracted from HTML alone.
    """
    print(f"[scraper] Fetching {url} …")
    html = fetch_html(url)
    data = extract_program_data(html, source_url=url)
    print("[scraper] Extraction complete.")
    return data


def store(document: Dict[str, Any]) -> str:
    """Insert *document* into MongoDB and return its inserted id string."""
    result = programs_collection.insert_one(document)
    return str(result.inserted_id)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Guide-to-Global scraper runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL of a university program page to scrape")
    group.add_argument(
        "--seed",
        action="store_true",
        help="Insert built-in sample programs into MongoDB (for development/testing)",
    )
    args = parser.parse_args()

    if args.seed:
        print("[runner] Seeding sample data …")
        for program in SAMPLE_PROGRAMS:
            inserted_id = store(program)
            print(f"  Inserted: {program['university']['name']} – {program['program']['name']} ({inserted_id})")
        print("[runner] Done.")
    else:
        data = scrape(args.url)
        inserted_id = store(data)
        print(f"[runner] Stored with id: {inserted_id}")
        print("[runner] NOTE: Please update university/program fields manually or via a secondary parser.")


if __name__ == "__main__":
    main()

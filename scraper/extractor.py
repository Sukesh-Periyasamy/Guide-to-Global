"""
HTML → structured JSON extractor.

Uses lightweight regex patterns to pull key admission details out of the
plain text of a university program page.  This approach is intentionally
simple (MVP) and can be replaced with LLM-based extraction later.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _html_to_text(html: str) -> str:
    """Strip HTML tags and return readable plain text."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _extract_ielts(text: str) -> Dict[str, Any]:
    """Return IELTS requirement dict extracted from *text*."""
    # Look for patterns like "IELTS 6.5", "IELTS score of 7.0", etc.
    match = re.search(r"IELTS[^0-9]*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if match:
        return {"required": True, "min_score": float(match.group(1))}
    if re.search(r"IELTS", text, re.IGNORECASE):
        return {"required": True, "min_score": None}
    return {"required": False, "min_score": None}


def _extract_toefl(text: str) -> Dict[str, Any]:
    """Return TOEFL requirement dict extracted from *text*."""
    match = re.search(r"TOEFL[^0-9]*([0-9]+)", text, re.IGNORECASE)
    if match:
        return {"required": True, "min_score": int(match.group(1))}
    if re.search(r"TOEFL", text, re.IGNORECASE):
        return {"required": True, "min_score": None}
    return {"required": False, "min_score": None}


def _extract_gre(text: str) -> Dict[str, Any]:
    """Return GRE requirement dict extracted from *text*."""
    if re.search(r"GRE\s+(?:is\s+)?required", text, re.IGNORECASE):
        return {"required": True, "recommended": False, "min_score": None}
    if re.search(r"GRE\s+(?:is\s+)?recommended", text, re.IGNORECASE):
        return {"required": False, "recommended": True, "min_score": None}
    if re.search(r"GRE", text, re.IGNORECASE):
        return {"required": False, "recommended": True, "min_score": None}
    return {"required": False, "recommended": False, "min_score": None}


def _extract_lor_count(text: str) -> int:
    """Return number of Letters of Recommendation mentioned in *text*."""
    match = re.search(
        r"([0-9]+)\s+(?:letters?\s+of\s+recommendation|LOR|recommendation\s+letters?)",
        text,
        re.IGNORECASE,
    )
    if match:
        return int(match.group(1))
    if re.search(r"letter[s]?\s+of\s+recommendation|LOR", text, re.IGNORECASE):
        return 1  # at least one mentioned
    return 0


def _extract_sop(text: str) -> bool:
    """Return True if a Statement of Purpose is mentioned in *text*."""
    return bool(re.search(r"statement\s+of\s+purpose|SOP", text, re.IGNORECASE))


def _extract_deadline(text: str) -> Optional[str]:
    """
    Attempt to extract an application deadline from *text*.

    Looks for common patterns such as "deadline: January 15, 2025" or
    "apply by 15 March 2025".
    """
    patterns = [
        r"deadline[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4})",
        r"apply by[:\s]+(\d{1,2} [A-Za-z]+ \d{4})",
        r"applications?\s+(?:due|close)[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4})",
        r"\b(\d{4}-\d{2}-\d{2})\b",  # ISO format
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_program_data(html: str, source_url: str = "") -> Dict[str, Any]:
    """
    Convert raw *html* into a structured dict that matches ProgramDocument.

    Most fields that cannot be reliably extracted are left as None/defaults so
    the caller (runner.py) can fill them in manually or via a secondary source.

    Args:
        html:       Raw HTML string of the program page.
        source_url: Original URL (stored as metadata.source).

    Returns:
        Dict matching the ProgramDocument schema (without _id).
    """
    text = _html_to_text(html)

    ielts = _extract_ielts(text)
    toefl = _extract_toefl(text)
    gre = _extract_gre(text)
    lor_count = _extract_lor_count(text)
    sop = _extract_sop(text)
    deadline = _extract_deadline(text)

    return {
        "university": {
            "name": "",
            "country": "",
            "city": "",
        },
        "program": {
            "name": "",
            "degree": "",
            "department": "",
            "duration": "",
        },
        "admission": {
            "status": "open",
            "intake": "",
            "deadline": deadline,
        },
        "requirements": {
            "ielts": ielts,
            "toefl": toefl,
            "gre": gre,
            "documents": {
                "lor": lor_count,
                "sop": sop,
                "resume": bool(re.search(r"\bresume\b|\bcv\b", text, re.IGNORECASE)),
                "transcript": bool(re.search(r"\btranscript\b", text, re.IGNORECASE)),
            },
        },
        "financial": {
            "tuition_fee": None,
            "scholarship_available": bool(
                re.search(r"\bscholarship\b|\bfellowship\b|\bfunding\b", text, re.IGNORECASE)
            ),
        },
        "links": {
            "admission_page": source_url or None,
            "program_page": source_url or None,
            "apply_link": None,
        },
        "raw_data": {
            "requirements_text": text[:2000],  # store first 2000 chars
            "description_text": None,
        },
        "metadata": {
            "last_scraped": datetime.now(timezone.utc).isoformat(),
            "source": source_url or None,
        },
    }

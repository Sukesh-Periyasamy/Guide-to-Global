"""
Scrapling client: fetches the raw HTML of a given URL.

Uses Scrapling's StaticFetcher for lightweight, fast HTML retrieval.
If you need JavaScript rendering, swap StaticFetcher for PlayWrightFetcher.
"""

from scrapling import StaticFetcher


def fetch_html(url: str) -> str:
    """
    Fetch the HTML content of *url* and return it as a plain string.

    Args:
        url: The fully-qualified URL to fetch.

    Returns:
        Raw HTML string.

    Raises:
        RuntimeError: If the page could not be fetched.
    """
    fetcher = StaticFetcher(auto_match=False)
    page = fetcher.fetch(url)
    if page is None:
        raise RuntimeError(f"Failed to fetch URL: {url}")
    return str(page.html_content)

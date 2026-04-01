"""
HTML parsing module using BeautifulSoup and lxml.
"""

from bs4 import BeautifulSoup


def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML string into a BeautifulSoup object.

    Args:
        html: The HTML string to parse

    Returns:
        BeautifulSoup object for traversing the document
    """
    return BeautifulSoup(html, "lxml")


def extract_title(soup: BeautifulSoup) -> str | None:
    """Extract the page title from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object

    Returns:
        Title string or None if not found
    """
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None


def extract_text(soup: BeautifulSoup) -> str:
    """Extract all text content from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object

    Returns:
        Combined text content
    """
    return soup.get_text(separator=" ", strip=True)

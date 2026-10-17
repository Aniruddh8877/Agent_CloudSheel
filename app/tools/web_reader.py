import re
import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("agent.tools.web_reader")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_webpage(url: str, max_chars: int = 4000) -> str:
    """
    Fetch and extract clean text and article contents from a public web page or URL.
    Use this tool after finding a relevant URL from web search to read its full details.

    Args:
        url: The full web URL (http:// or https://) to read.
        max_chars: Maximum characters of text to return (default is 4000).
    """
    if not url or not url.startswith(("http://", "https://")):
        return "Error: Invalid URL. URL must start with http:// or https://"

    try:
        with httpx.Client(timeout=12.0, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract title
        title_tag = soup.find("title")
        page_title = title_tag.get_text(strip=True) if title_tag else "No Title Found"

        # Remove irrelevant elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "aside"]):
            element.decompose()

        # Find main article container if available
        article = soup.find("article") or soup.find("main") or soup.find("body") or soup
        text = article.get_text(separator="\n", strip=True)

        # Clean multiple spaces and blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... [Content truncated at {max_chars} characters]"

        return f"=== Webpage Content from {url} ===\nTitle: {page_title}\n\n{text}"
    except httpx.HTTPStatusError as e:
        return f"Failed to fetch {url}: HTTP {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return f"Failed to fetch webpage at {url}: {str(e)}"

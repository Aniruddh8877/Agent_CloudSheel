import logging
from ddgs import DDGS

logger = logging.getLogger("agent.tools.web_search")

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the live web using DuckDuckGo for recent news, technical docs, current events, or general queries.
    Returns titles, descriptions, and URLs of relevant search results.
    
    Args:
        query: The search keywords or query string.
        max_results: Maximum number of search results to retrieve (default is 5).
    """
    if not query or not query.strip():
        return "Error: Empty search query provided."

    query = query.strip()
    try:
        results = []
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for i, r in enumerate(raw_results, 1):
                title = r.get("title", "No Title")
                href = r.get("href", "")
                body = r.get("body", "")
                results.append(f"[{i}] {title}\nURL: {href}\nSnippet: {body}")

        if not results:
            return f"No search results found for query: '{query}'."

        return f"Found {len(results)} search results for '{query}':\n\n" + "\n\n".join(results)
    except Exception as e:
        logger.error(f"Search failed for '{query}': {e}")
        return f"Web search error: {str(e)}"

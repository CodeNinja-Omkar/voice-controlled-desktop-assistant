import webbrowser
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Opened {url}."
    except Exception as e:
        logger.error("Failed to open URL %s: %s", url, e)
        return "Could not open the browser."


def search_web(query: str) -> str:
    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://www.google.com/search?q={encoded}"
    return open_url(url)
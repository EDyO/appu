from loguru import logger
import feedparser
def validate_feed(url) -> None:
    logger.info(f"Validating feed {url}")
    feed = feedparser.parse(url)
    if feed.bozo:
        logger.error(f"Feed {url} is invalid")
        raise SystemExit(1)
    
    num_entries = len(feed.entries)
    title = feed.feed.title
    logger.info(f"Feed {url} has title `{title}` and contains {num_entries} entries")
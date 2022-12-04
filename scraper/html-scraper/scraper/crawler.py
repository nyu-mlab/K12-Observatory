""" tries to understand what the page is about
including process and analyze textual content + key content tags and attributes
"""
import scraper.task
from scraper import crawler_middleware


default_middleware = (
    crawler_middleware.BinaryContent,
    crawler_middleware.Depth,
    crawler_middleware.ThirdParty,
    crawler_middleware.Referer,
)


class Crawler:
    """Crawler"""

    def __init__(self, n_worker=1, middleware=default_middleware):
        pass

    def parse(self, task: scraper.task.Task):
        if task.metadata.get("drop"):
            return None

        pass

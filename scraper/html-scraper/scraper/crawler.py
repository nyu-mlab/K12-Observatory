""" tries to understand what the page is about
including process and analyze textual content + key content tags and attributes
"""
import scraper.crawler_middleware as middleware
import scraper.task

middleware = [
    middleware.BinaryContent,
    middleware.Depth,
    middleware.ThirdParty,
    middleware.Referer,
]


class Crawler:

    def __init__(self, n_worker=1):
        pass

    def parse(self, task: scraper.task.Task):
        if task.metadata.get("drop"):
            return None

        pass

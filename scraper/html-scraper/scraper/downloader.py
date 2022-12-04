""" visit (or "crawl") the page to find out what's on it
"""
import scraper.downloader_middleware as middleware
import scraper.task

default_middleware = (
    middleware.BinaryContent,
    middleware.HttpError,
    #middleware.HttpProxy,  # XXX: do we need this?
    middleware.JsCrawl,
    #middleware.UserAgent,  # XXX: do we need this?
)


class Downloader:

    def __init__(self, n_worker=1, middleware=default_middleware):
        pass

    def process(self, task: scraper.task.Task):
        if task.metadata.get("drop"):
            return None

        pass

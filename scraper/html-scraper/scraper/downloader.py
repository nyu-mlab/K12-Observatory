""" visit (or "crawl") the page to find out what's on it
"""
import scraper.task
from scraper import downloader_middleware

default_middleware = (
    downloader_middleware.BinaryContent,
    downloader_middleware.HttpError,
    #downloader_middleware.HttpProxy,  # XXX: do we need this?
    downloader_middleware.JsCrawl,
    #downloader_middleware.UserAgent,  # XXX: do we need this?
)


class Downloader:

    def __init__(self, n_worker=1, middleware=default_middleware):
        pass

    def process(self, task: scraper.task.Task):
        if task.metadata.get("drop"):
            return None

        pass

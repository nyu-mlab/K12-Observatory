""" visit (or "crawl") the page to find out what's on it
"""
import graphlib
import multiprocessing as mp

import scraper.task
from scraper import downloader_middleware

default_middleware = graphlib.TopologicalSorter({
    downloader_middleware.BinaryContent(): (),
    downloader_middleware.HttpError(): (),
    #downloader_middleware.HttpProxy(): (),  # XXX: do we need this?
    downloader_middleware.JsCrawl(): (),
    #downloader_middleware.UserAgent(): (),  # XXX: do we need this?
})


class Downloader:
    """Downloader"""

    def __init__(self,
                 n_worker: int = None,
                 middleware: graphlib.TopologicalSorter = default_middleware):
        middleware.prepare()
        self.middleware = middleware

    def process(self, task: scraper.task.Task):
        if task.metadata.get("drop"):
            return None

        pass

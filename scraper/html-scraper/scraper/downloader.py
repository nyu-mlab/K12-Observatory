""" visit (or "crawl") the page to find out what's on it
"""
import copy
import graphlib

import requests
import scraper.task

from scraper import component
from scraper import downloader_middleware

default_middleware = graphlib.TopologicalSorter({
    downloader_middleware.BinaryContent(): (),
    downloader_middleware.HttpError(): (),
    #downloader_middleware.HttpProxy(): (),  # XXX: do we need this?
    downloader_middleware.JsCrawl(): (),
    #downloader_middleware.UserAgent(): (),  # XXX: do we need this?
})


class Downloader(component.Component):
    """Downloader"""

    @classmethod
    def _process(cls, task: scraper.task.Task) -> scraper.task.Task:
        if task.metadata.get("drop"):
            return None

        with requests.Session() as session:
            task.response = session.send(task.request.prepare(),
                                         timeout=task.timeout)
        # TODO: FIXME: send request

        middleware = copy.copy(cls.middleware)
        # TODO: parallelize with DAG
        for mw_task in middleware.static_order():
            mw_task.process(task)

        return task

    def process(self, task: scraper.task.Task):

        def callback(result):
            # TODO: don't use return-None as request-filter behavior
            if result is not None:
                self.finished_queue.put(result)

        def error_handler(err):
            raise err  #TODO:

        self.worker_pool.apply_async(self._process,
                                     task,
                                     callback=callback,
                                     error_callback=error_handler)

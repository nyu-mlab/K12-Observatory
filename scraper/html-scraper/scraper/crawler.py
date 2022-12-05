""" tries to understand what the page is about
including process and analyze textual content + key content tags and attributes
"""
import copy
import graphlib

import scraper.task

from scraper import component
from scraper import crawler_middleware

# TODO: replace this with something faster like "lxml" or "parsel"
from bs4 import BeautifulSoup

default_middleware = graphlib.TopologicalSorter({
    crawler_middleware.BinaryContent(): (),
    crawler_middleware.Depth(): (),
    crawler_middleware.ThirdParty(): (),
    crawler_middleware.Referer(): (),
})


class Crawler(component.Component):
    """Crawler"""

    @classmethod
    def _process(cls, task: scraper.task.Task) -> scraper.task.Task:
        if task.metadata.get("drop"):
            return None

        soup = BeautifulSoup(task.response.text, features="html.parser")
        # TODO: FIXME: parse html to get urls

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

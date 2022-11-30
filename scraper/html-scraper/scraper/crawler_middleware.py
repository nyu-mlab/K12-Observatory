""" Crawler Middleware
post-crawler processing plugins
"""
import abc
import scraper.task


class Middleware(abc.ABC):

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        pass


class Depth(Middleware):
    pass


class Offsite(Middleware):
    """Filter out second level third party site requests"""
    pass


class BinaryContent(Middleware):
    """Filter out requests with binary extensions before sending request"""
    pass

""" Downloader Middleware
post-downloader processing plugins
"""
import abc
import scraper.task


class Middleware(abc.ABC):

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        pass


class HttpError(Middleware):
    """Filter out unsuccessful (erroneous) HTTP responses"""
    pass


class JsCrawl(Middleware):
    # TODO: TEMP:
    # NOTE: REF: https://developers.google.com/search/docs/ajax-crawling/docs/getting-started
    pass


class BinaryContent(Middleware):
    """Filter out binary content via "Content-Type" header before parsing"""
    pass

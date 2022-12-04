""" Downloader Middleware
post-downloader processing plugins
"""
import abc
import pathlib
import urllib.parse

import scraper.task


class Middleware(abc.ABC):

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        pass


class HttpError(Middleware):
    """Filter out unsuccessful (erroneous) HTTP responses"""

    def process(self, task):
        if not task.response.ok:
            task.metadata["drop"] = True  # Drop this request


class JsCrawl(Middleware):
    # TODO: TEMP:
    # NOTE: REF: https://developers.google.com/search/docs/ajax-crawling/docs/getting-started
    def process(self, task):
        pass


class BinaryContent(Middleware):
    """Filter out binary content via "Content-Type" header before parsing"""

    BINARY_CONTENT_EXTENSIONS = [
        "gif", "jpg", "png", "doc", "docx", "xls", "xlsx", "pdf", "mp4", "mp3",
        "mov", "flv"
    ]

    def process(self, task):
        resource_path = urllib.parse.urlparse(task.response.url).path
        if pathlib.PurePath(
                resource_path).suffix in self.BINARY_CONTENT_EXTENSIONS:
            task.metadata["drop"] = True  # Drop this request


# TODO: crawler-drop-decorator wraps and checks for metadata["drop"] then acts accordingly

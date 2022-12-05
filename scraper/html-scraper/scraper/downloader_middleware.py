""" Downloader Middleware
post-downloader processing plugins
"""
import abc
import pathlib
import urllib.parse

import scraper.task


class Middleware(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def process(cls, task: scraper.task.Task):
        pass


# TODO: crawler-drop-decorator wraps and checks for metadata["drop"] then acts accordingly


class HttpError(Middleware):
    """Filter out unsuccessful (erroneous) HTTP responses"""

    @classmethod
    def process(cls, task):
        if not task.response.ok:
            task.metadata["drop"] = True  # Drop this request


class JsCrawl(Middleware):
    # TODO: TEMP:
    # NOTE: REF: https://developers.google.com/search/docs/ajax-crawling/docs/getting-started

    @classmethod
    def process(cls, task):  # pragma: no cover
        pass


class BinaryContent(Middleware):
    """Filter out binary content via "Content-Type" header before parsing"""

    BINARY_CONTENT_EXTENSIONS = [
        "gif", "jpg", "png", "doc", "docx", "xls", "xlsx", "pdf", "mp4", "mp3",
        "mov", "flv"
    ]

    @classmethod
    def process(cls, task):
        resource_path = urllib.parse.urlparse(task.response.url).path
        resource_extension = pathlib.PurePath(resource_path).suffix

        if any(binary_extension in resource_extension
               for binary_extension in cls.BINARY_CONTENT_EXTENSIONS):
            task.metadata["drop"] = True  # Drop this request

""" Downloader Middleware
post-downloader processing plugins
"""
import abc
import pathlib
import urllib.parse

import scraper.task
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
module_shortname = "downloader_mw" or __name__.rsplit(".", maxsplit=1)[-1]


class Middleware(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def process(cls, task: scraper.task.Task):
        raise NotImplementedError


# TODO: crawler-drop-decorator wraps and checks for metadata["drop"] then acts accordingly


class HttpError(Middleware):
    """Filter out unsuccessful (erroneous) HTTP responses"""

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="http_status"))
    def process(cls, task):
        # TODO: do more checking for subcases?
        if not task.response.ok:
            task.metadata["drop"] = True


class JsCrawl(Middleware):
    # TODO: TEMP:
    # NOTE: REF: https://developers.google.com/search/docs/ajax-crawling/docs/getting-started

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="js_render"))
    def process(cls, task):
        pass  # pragma: no cover


class BinaryContent(Middleware):
    """Filter out binary content via "Content-Type" header before parsing"""

    BINARY_CONTENT_EXTENSIONS = [
        "gif", "jpg", "png", "doc", "docx", "xls", "xlsx", "pdf", "mp4", "mp3",
        "mov", "flv"
    ]

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="binary_content"))
    def process(cls, task):
        resource_path = urllib.parse.urlparse(task.response.url).path
        resource_extension = pathlib.PurePath(resource_path).suffix

        if any(binary_extension in resource_extension
               for binary_extension in cls.BINARY_CONTENT_EXTENSIONS):
            task.metadata["drop"] = True

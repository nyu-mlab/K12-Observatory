""" Crawler Middleware
post-crawler processing plugins
"""
import abc
import functools
import urllib.parse

import scraper.task
import tldextract
from opentelemetry import trace

# TODO: do some parallelization, use DAG to explore chances
# (need partial order with DAG because some operations like depth-based-priority-modifying needs to be executed after depth-middleware)

tracer = trace.get_tracer(__name__)
module_shortname = "crawler_mw" or __name__.rsplit(".", maxsplit=1)[-1]


class Middleware(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def process(cls, task: scraper.task.Task):
        raise NotImplementedError


# TODO: enqueue-drop-decorator wraps and checks for metadata["drop"] then acts accordingly


class Depth(Middleware):

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="depth"))
    def process(cls, task):
        if not (current_depth := task.metadata.get("depth")):
            current_depth = 0
            task.metadata["depth"] = current_depth

        for spawned_task in task.results:
            spawned_task.metadata["depth"] = current_depth + 1


class Referer(Middleware):

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="referer"))
    def process(cls, task):
        if not (referer := task.metadata.get("referer")):
            referer = ""
            task.metadata["referer"] = referer

        for spawned_task in task.results:
            spawned_task.metadata["referer"] = task.request.url


class ThirdParty(Middleware):
    """Filter out second level third party site requests"""

    # FIXME: what if the root request itself is redirected right from the start? shall we update upon root-request redirection or use task.response.url for root_domain instead?

    @staticmethod
    @tracer.start_as_current_span("get_registered_domain")
    @functools.lru_cache  # FIXME: default size=128 will cause thrashing when target domains are distributed # TODO: tune size
    @tracer.start_as_current_span("get_registered_domain-cached")
    def get_registered_domain(url):
        # TODO: can we replace "tldextract"?
        return tldextract.extract(url).registered_domain

    @staticmethod
    @tracer.start_as_current_span("get_hostname")
    def get_hostname(url):
        hostname = urllib.parse.urlparse(url).hostname
        return ThirdParty.get_registered_domain(hostname)

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="third_party"))
    def process(cls, task):
        """don't visit any links from third party pages"""
        # TODO: should we do "drop third party links from third party pages" instead?

        if not (root_hostname := task.metadata.get("root_hostname")):
            root_hostname = cls.get_hostname(task.request.url)
            task.metadata["root_hostname"] = root_hostname

        is_3rd_party = root_hostname != cls.get_hostname(task.response.url)
        if is_3rd_party:
            task.results.clear()
        else:
            for spawned_task in task.results:
                spawned_task.metadata["root_hostname"] = root_hostname


class BinaryContent(Middleware):
    """Filter out requests with binary extensions before building request"""

    BINARY_CONTENT_TYPES = ["pdf", "zip", "audio", "image", "video"]

    @classmethod
    @tracer.start_as_current_span(module_shortname,
                                  attributes=dict(middleware="binary_content"))
    def process(cls, task):
        content_type = task.response.headers["Content-Type"]
        if any(binary_type in content_type
               for binary_type in cls.BINARY_CONTENT_TYPES):
            task.metadata["drop"] = True

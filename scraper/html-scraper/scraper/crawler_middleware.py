""" Crawler Middleware
post-crawler processing plugins
"""
import abc
import functools
import urllib.parse
import scraper.task


class Middleware(abc.ABC):

    @abc.abstractmethod
    def process(self, task: scraper.task.Task):
        pass


class Depth(Middleware):

    def process(self, task):
        if not (current_depth := task.metadata.get("depth")):
            current_depth = 0
            task.metadata["depth"] = current_depth

        for spawned_task in task.results:  # discovered URLs
            spawned_task.metadata["depth"] = current_depth + 1


class Referer(Middleware):

    def process(self, task):
        pass


class ThirdParty(Middleware):
    """Filter out second level third party site requests"""

    # FIXME: what if the root request itself is redirected right from the start? shall we update upon root-request redirection or use task.response.url for root_domain instead?

    @staticmethod
    @functools.lru_cache
    def get_registered_domain(url):
        # FIXME: import tldextract
        # TODO: can we replace "tldextract"?
        return tldextract.extract(url).registered_domain

    @staticmethod
    def get_hostname(url):
        hostname = urllib.parse.urlparse(url).hostname
        return ThirdParty.get_registered_domain(hostname)

    def process(self, task):
        """don't visit any links from third party pages"""
        # TODO: should we do "drop third party links from third party pages" instead?

        if not (root_hostname := task.metadata.get("root_hostname")):
            root_hostname = self.get_hostname(task.request.url)
            task.metadata["root_hostname"] = root_hostname

        is_3rd_party = root_hostname != self.get_hostname(task.response.url)
        if is_3rd_party:
            task.results.clear()
        else:
            for spawned_task in task.results:
                spawned_task.metadata["root_hostname"] = root_hostname


class BinaryContent(Middleware):
    """Filter out requests with binary extensions before sending request"""
    pass

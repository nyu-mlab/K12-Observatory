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

    def process(self, task):
        if not (current_depth := task.metadata.get("depth")):
            task.metadata["depth"] = 0

        for spawned_task in task.results:  # discovered URLs
            spawned_task.metadata["depth"] = current_depth + 1


class Offsite(Middleware):
    """Filter out second level third party site requests"""
    pass


class BinaryContent(Middleware):
    """Filter out requests with binary extensions before sending request"""
    pass

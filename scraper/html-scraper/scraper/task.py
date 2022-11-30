""" Task
"""
import requests


class Task:

    def __init__(
        self,
        request: requests.Request,
        *,
        timeout=60,
        priority=1,
        #referer=None, # TODO: move this to a middleware and log it in self.metadata
    ):
        self.request = request
        self.timeout = timeout
        self.priority = priority  # additional priority for scheduler to use (e.g. can be used to crawl shallow pages first or deep pages first)
        # TODO: consider doing "request-fingerprinting" to filter out duplicate requests or cache them
        # TODO: can designate outgoing interface (binded address) or should we delegate to scheduling stage?
        # TODO: log timestamp before sending
        # TODO: record self.response.elapsed info for scheduling

        self.response: requests.Response = None
        self.results: list[Task] = []
        self.metadata = {
        }  # TODO: consider dropping "metadata" and use "self.<var>" directly for middleware data instead, since member variables does not need to be explicitly defined at __init__ anyway

        # TODO: in some middleware: if is root request (no previous value set), set depth=1, root_hostname=hostname

    # TODO: sort all property methods

""" Task
"""
import requests


class Task:
    # TODO: record self.response.elapsed info for scheduling

    class Request:

        def __init__(
            self,
            request: requests.Request,
            timeout,
            priority,
        ):
            self.request = request
            self.timeout = timeout
            self.priority = priority  # additional priority for scheduler to use (e.g. can be used to crawl shallow pages first or deep pages first)
            # TODO: consider doing "request-fingerprinting" to filter out duplicate requests or cache them
            # TODO: can designate outgoing interface (binded address) or should we delegate to scheduling stage?

        # TODO: log timestamp before sending

    def __init__(
        self,
        request: requests.Request,
        *,
        timeout=60,
        priority=1,
        #referer=None, # TODO: move this to a middleware and log it in self.metadata
        #root_request_hostname=None,  # TODO: move this to DropSecondLevelThirdPartyMiddleware and log it in self.metadata
    ):
        self.request = self.Request(request, timeout, priority)
        self.response = None
        self.metadata = {}

        # TODO: in some middleware: if is root request (no previous value set), set depth=1, root_hostname=hostname


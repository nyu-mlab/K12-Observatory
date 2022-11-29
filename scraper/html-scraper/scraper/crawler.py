""" tries to understand what the page is about
this includes processing and analyzing the textual content and key content tags and attributes
"""


middleware = [
    #CookiesMiddleware,
    HttpProxyMiddleware,
    UserAgentMiddleware,
    JsCrawlMiddleware,  # https://developers.google.com/search/docs/ajax-crawling/docs/getting-started
    BinaryContentMiddleware,  # Filter out binary content via "Content-Type" header before parsing
]


class Crawler:

    def __init__(self, n_worker=1):
        pass

    def parse(self, response):
        pass

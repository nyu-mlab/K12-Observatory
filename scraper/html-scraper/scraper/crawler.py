""" tries to understand what the page is about
including process and analyze textual content + key content tags and attributes
"""
import scraper.crawler_middleware as middleware

middleware = [
    middleware.BinaryContent,
    middleware.Depth,
    middleware.Offsite,
    middleware.Referer,
]


class Crawler:

    def __init__(self, n_worker=1):
        pass

    def parse(self, response):
        pass

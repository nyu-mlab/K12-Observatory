""" finding out what pages exist on the web, aka "URL discovery"
visit (or "crawl") the page to find out what's on it
"""

middleware = [
    DepthMiddleware,
    HttpErrorMiddleware,  # Filter out unsuccessful (erroneous) HTTP responses
    OffsiteMiddleware,  # Filter out second level third party site requests
    BinaryContentMiddleware,  # Filter out requests with binary extensions before sending request
]


class Downloader:

    def __init__(self, n_worker=1):
        pass

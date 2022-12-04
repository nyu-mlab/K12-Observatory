import pytest

import scraper.downloader_middleware as middleware
import scraper.task


# TODO: parametrize fixture with different tasks
@pytest.fixture(scope="function", params=["""TODO:"""])
def task():
    _: scraper.task.Task
    # TODO: monkeypatch requests.Response
    pass


class TestBinaryContentMiddleware:
    # TODO:
    _ = middleware.BinaryContent


class TestHttpErrorMiddleware:
    # TODO:
    _ = middleware.HttpError


@pytest.mark.skip(reason="yet to be integrated with the JS crawler")
class TestJsCrawlMiddleware:
    # TODO:
    _ = middleware.JsCrawl

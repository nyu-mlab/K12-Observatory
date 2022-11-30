import pytest
import scraper.crawler_middleware as middleware
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


class TestDepthMiddleware:
    # TODO:
    _ = middleware.Depth


class TestRefererMiddleware:
    # TODO:
    _ = middleware.Referer


class TestOffsiteMiddleware:
    # TODO:
    _ = middleware.Offsite

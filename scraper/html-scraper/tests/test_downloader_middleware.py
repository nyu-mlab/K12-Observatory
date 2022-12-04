import pytest
import requests
import scraper.downloader_middleware as middleware
import scraper.task


# TODO: parametrize fixture with different tasks
@pytest.fixture
def basic_task():

    def _basic_task():
        url = "http://localhost/resource"
        task = scraper.task.Task(requests.Request(url=url))
        response = requests.Response()
        response.url = url
        task.response = response

        return task

    return _basic_task


class TestMiddlewareBaseClass:

    def test_base_class_is_abstract(self):
        with pytest.raises(TypeError):
            middleware.Middleware()

    def test_duck_type_methods(self):
        # exists an abstract classmethod function called "process"
        assert callable(middleware.Middleware.process)
        assert "process" in middleware.Middleware.__abstractmethods__
        middleware.Middleware.process(None)


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

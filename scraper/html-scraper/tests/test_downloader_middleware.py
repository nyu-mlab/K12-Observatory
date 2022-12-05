import http
import mimetypes
import pathlib
import urllib.parse

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

    def test_process(self, basic_task):
        for file_extension in (mimetypes.types_map |
                               mimetypes.common_types).keys():
            task = basic_task()

            parsed_request = urllib.parse.urlparse(task.request.url)
            task.request.url = urllib.parse.urlunparse((
                parsed_request.scheme,
                parsed_request.netloc,
                str(
                    pathlib.PurePath(
                        parsed_request.path).with_suffix(file_extension)),
                parsed_request.params,
                parsed_request.query,
                parsed_request.fragment,
            ))

            parsed_response = urllib.parse.urlparse(task.response.url)
            task.response.url = urllib.parse.urlunparse((
                parsed_response.scheme,
                parsed_response.netloc,
                str(
                    pathlib.PurePath(
                        parsed_response.path).with_suffix(file_extension)),
                parsed_response.params,
                parsed_response.query,
                parsed_response.fragment,
            ))

            middleware.BinaryContent.process(task)

            if any(bin_ext in file_extension for bin_ext in
                   middleware.BinaryContent.BINARY_CONTENT_EXTENSIONS):
                assert task.metadata["drop"] is True
            else:
                # some False value or the "drop" key doesn't even exist
                if hasattr(task.metadata, "drop"):
                    assert bool(task.metadata["drop"]) is not False
                else:
                    with pytest.raises(KeyError):
                        print(task.metadata["drop"])


class TestHttpErrorMiddleware:

    def test_process(self, basic_task):
        for status_code in (status.value for status in http.HTTPStatus):
            task = basic_task()
            task.response.status_code = status_code
            middleware.HttpError.process(task)

            if status_code < 400:
                # some False value or the "drop" key doesn't even exist
                if hasattr(task.metadata, "drop"):
                    assert bool(task.metadata["drop"]) is not False
                else:
                    with pytest.raises(KeyError):
                        print(task.metadata["drop"])
            else:
                assert task.metadata["drop"] is True


@pytest.mark.skip(reason="yet to be integrated with the JS crawler")
class TestJsCrawlMiddleware:
    # TODO:
    _ = middleware.JsCrawl

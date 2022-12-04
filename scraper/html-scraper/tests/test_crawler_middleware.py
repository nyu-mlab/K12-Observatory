import mimetypes

import pytest
import requests
import scraper.crawler_middleware as middleware
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
        for mime_type in (mimetypes.types_map |
                          mimetypes.common_types).values():
            task = basic_task()
            task.response.headers["Content-Type"] = mime_type
            middleware.BinaryContent.process(task)

            if any(bin_type in mime_type for bin_type in
                   middleware.BinaryContent.BINARY_CONTENT_TYPES):
                assert task.metadata["drop"] is True
            else:
                # some False value or the "drop" key doesn't even exist
                if hasattr(task.metadata, "drop"):
                    assert bool(task.metadata["drop"]) is not False
                else:
                    with pytest.raises(KeyError):
                        print(task.metadata["drop"])


class TestDepthMiddleware:

    def test_process_root_requests(self, basic_task):
        """Init root request depth to zero"""

        root_task = basic_task()
        with pytest.raises(KeyError):
            print(root_task.metadata["depth"])

        middleware.Depth.process(root_task)
        assert root_task.metadata["depth"] == 0

    def test_process_non_root_requests(self, basic_task):
        """Preserve non-root request depth"""

        # TODO: should we validate depth to be a Natural Number?
        non_root_task = basic_task()
        non_root_task.metadata["depth"] = 1
        depth = non_root_task.metadata["depth"]

        middleware.Depth.process(non_root_task)
        assert non_root_task.metadata["depth"] == depth

    def test_increase_children_depth(self, basic_task):
        # root/non-root requests could have different code paths,
        # should be tested separately

        # root request
        root_task = basic_task()
        with pytest.raises(KeyError):
            print(root_task.metadata["depth"])

        root_task.results = list((scraper.task.Task(
            requests.Request(url="http://localhost/resource2")),)) * 4

        middleware.Depth.process(root_task)
        assert all(
            subtask.metadata["depth"] == 1 for subtask in root_task.results)

        # non root request
        non_root_task = basic_task()
        non_root_task.metadata["depth"] = 1
        depth = non_root_task.metadata["depth"]

        non_root_task.results = list((scraper.task.Task(
            requests.Request(url="http://localhost/resource2")),)) * 4

        middleware.Depth.process(non_root_task)
        assert all(subtask.metadata["depth"] == depth + 1
                   for subtask in non_root_task.results)


class TestRefererMiddleware:

    def test_process_root_requests(self, basic_task):
        """Init root request referer to empty string"""

        root_task = basic_task()
        with pytest.raises(KeyError):
            print(root_task.metadata["referer"])

        middleware.Referer.process(root_task)
        assert root_task.metadata["referer"] == ""

    def test_process_non_root_requests(self, basic_task):
        """Preserve non-root request referer"""

        # TODO: should we validate referer to be a valid URL?
        non_root_task = basic_task()
        non_root_task.metadata["referer"] = "http://jabba.the.hut/resource"
        referer = non_root_task.metadata["referer"]

        middleware.Referer.process(non_root_task)
        assert non_root_task.metadata["referer"] == referer

    def test_increase_children_depth(self, basic_task):
        # root/non-root requests could have different code paths,
        # should be tested separately

        # root request
        root_task = basic_task()
        with pytest.raises(KeyError):
            print(root_task.metadata["referer"])
        root_url = root_task.request.url

        root_task.results = list((scraper.task.Task(
            requests.Request(url="http://localhost/resource2")),)) * 4

        middleware.Referer.process(root_task)
        assert all(subtask.metadata["referer"] == root_url
                   for subtask in root_task.results)

        # non root request
        non_root_task = basic_task()
        non_root_task.metadata["referer"] = "http://jabba.the.hut/resource"
        request_url = non_root_task.request.url

        non_root_task.results = list((scraper.task.Task(
            requests.Request(url="http://localhost/resource2")),)) * 4

        middleware.Referer.process(non_root_task)
        assert all(subtask.metadata["referer"] == request_url
                   for subtask in non_root_task.results)


class TestThirdPartyMiddleware:

    @pytest.mark.skip("WIP")
    def test_process(self, basic_task):
        task = basic_task()
        processed_task = middleware.ThirdParty.process(task)

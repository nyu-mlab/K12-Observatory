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


class TestBinaryContentMiddleware:
    # TODO:
    _ = middleware.BinaryContent


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
            requests.Request(url="http://localhost/resource")),)) * 4

        middleware.Depth.process(root_task)
        assert all(
            subtask.metadata["depth"] == 1 for subtask in root_task.results)

        # non root request
        non_root_task = basic_task()
        non_root_task.metadata["depth"] = 1
        depth = non_root_task.metadata["depth"]

        non_root_task.results = list((scraper.task.Task(
            requests.Request(url="http://localhost/resource")),)) * 4

        middleware.Depth.process(non_root_task)
        assert all(subtask.metadata["depth"] == depth + 1
                   for subtask in non_root_task.results)


class TestRefererMiddleware:
    # TODO:
    _ = middleware.Referer


class TestThirdPartyMiddleware:
    # TODO:
    _ = middleware.ThirdParty

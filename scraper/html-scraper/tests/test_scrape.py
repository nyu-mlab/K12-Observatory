import concurrent.futures
import graphlib
import math
import pathlib
import re

import mock.website
import pytest
import requests

import scraper

Url = mock.website.Url
mock_site = mock.website.site_generator


class TestMockSite:
    """fake site generator"""

    def test_server_reply(self, mock_site):
        """
        main---page1 (O)
        main---page2 (O)
        main---page3 (O)
        """

        main_site = mock_site(
            "main",
            {
                "page1": (Url("main", "page2"),),
                "page2": (Url("main", "page3"),),
                "page3": (),
            },
        )

        for i in range(1, 4):
            path = Url("main", f"page{i}")
            print(path, repr(path), str(path))
            r = requests.get(str(path), timeout=(0.1, 0.1))

            assert r.ok
            # NOTE: keep validation scheme simple
            assert re.search(fr"<title>page{i}</title>", r.text)


class TestDownloader:

    # TODO: test scraping mock server for single page, then halt and inspect
    @pytest.mark.skip(reason="WIP")
    def test_scrape_single_page(self, mock_site):
        pass

    # TODO: test result persistence

    def test_drop_dead_links(self, mock_site):
        """
        main---page1      (O)
         |- main---page2  (X)
        """

        main_site = mock_site(
            "main",
            {
                "page1": (Url("main", "page2")),
            },
        )

    def test_PLACEHOLDER(self):
        scraper.Downloader(None)


class TestCrawler:

    # TODO: test scraping mock server for automated-whole-site scraping, then inspect site map
    def test_crawls_links(self, mock_site):
        """
        main---page1         (O)
         |- main---page2     (O)
         |   |- main---page4 (O)
         |
         |- main---page3     (O)
             |- main---page5 (O)
        """
        main_site = mock_site(
            "main",
            {
                "page1": (Url("main", "page2"), Url("main", "page3")),
                "page2": (Url("main", "page4"),),
                "page3": (Url("main", "page5"),),
                "page4": (),
                "page5": (),
            },
        )

    def test_drops_second_level_third_party_links(self, mock_site):
        """
        main---page1                (O)
         |- 3rd-party-1---page1     (O)
         |   |- 3rd-party-1---page2 (X)
         |   |- 3rd-party-2---page1 (X)
         |
         |- 3rd-party-3---page1     (O)
             |- main---page2        (X)  TODO: should we crawl this?
        """

        main_site = mock_site(
            "main",
            {
                "page1": (Url("third_party_1", "page1")),
                "page2": (),
            },
        )
        third_party_site1 = mock_site(
            "third_party_1",
            {
                "page1": (
                    Url("third_party_1", "page2"),
                    Url("third_party_2", "page1"),
                ),
                "page2": (),
            },
        )
        third_party_site2 = mock_site(
            "third_party_2",
            {
                "page1": (),
            },
        )
        third_party_site3 = mock_site(
            "third_party_3",
            {
                "page1": (Url("main", "page2")),
            },
        )

    def test_PLACEHOLDER(self):
        scraper.Crawler(None)


class TestScheduler:
    # TODO: move to its own file
    pass
    # TODO: scheduler behavior
    # TODO: queue persistence


def is_prime(n: int):
    if n < 2:
        return False
    elif n == 2:
        return True
    elif n % 2 == 0:
        return False
    else:
        sqrt_n = int(math.floor(math.sqrt(n)))
        for i in range(3, sqrt_n + 1, 2):
            if n % i == 0:
                return False
        return True


class TestWorker:
    # TODO: move to its own file

    class BasicWorker(scraper.processor.BaseWorker):

        def process(self, task):
            # Look for primes
            primes = {
                112272535095293: True,
                112582705942171: True,
                115280095190773: True,
                115797848077099: True,
                1099726899285419: False,
            }
            with self.worker_pool as executor:
                for number, prime_or_not in zip(primes,
                                                executor.map(is_prime, primes)):
                    assert primes[number] == prime_or_not

    def test_creation(self, monkeypatch):
        Worker = scraper.processor.BaseWorker
        worker_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        with monkeypatch.context() as m:
            m.setattr(Worker, "__abstractmethods__", frozenset())
            # assert no exceptions when constructing with graph/dict/tuple/list
            for mw in (
                    graphlib.TopologicalSorter({
                        scraper.crawler_middleware.Depth():
                            (scraper.crawler_middleware.Referer(),),
                    }),
                {
                    scraper.crawler_middleware.Depth():
                        (scraper.crawler_middleware.Referer(),),
                },
                (
                    scraper.crawler_middleware.Depth(),
                    scraper.crawler_middleware.Referer(),
                ),
                [
                    scraper.crawler_middleware.Depth(),
                    scraper.crawler_middleware.Referer(),
                ],
                    tuple((scraper.crawler_middleware.Depth(),)),
                    list((scraper.crawler_middleware.Depth(),)),
                    None,
                [],  # empty list
                [1],  # list with one item
            ):
                Worker(mw, worker_pool)

            # assert exceptions  # FIXME: is this necessary?
            for mw in [
                    1,
            ]:
                with pytest.raises(ValueError, match=f"{type(mw)}"):
                    Worker(mw, worker_pool)

    @pytest.mark.worker_pool
    @pytest.mark.slow
    def test_thread_workers(self):
        worker_pool = concurrent.futures.ThreadPoolExecutor()
        worker = self.BasicWorker([], worker_pool)
        worker.process(None)

    @pytest.mark.worker_pool
    @pytest.mark.slow
    def test_process_workers(self, monkeypatch):
        # Requires the tests directory to be importable from PYTHON_PATH due to
        # multiprocessing module pickling everything
        with monkeypatch.context() as m:
            m.syspath_prepend(pathlib.PurePath(__file__).parent.parent)
            worker_pool = concurrent.futures.ProcessPoolExecutor()
            worker = self.BasicWorker([], worker_pool)
            worker.process(None)

import graphlib
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


class TestWorker:
    # TODO: move to its own file

    def test_creation(self, monkeypatch):
        Worker = scraper.processor.BaseWorker
        monkeypatch.setattr(Worker, "__abstractmethods__", frozenset())
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
        ):
            Worker(middleware=mw, n_worker=None)

        # assert exceptions
        for mw in (
                1,
                "abc",
        ):
            with pytest.raises(ValueError, match=f"{type(mw)}"):
                Worker(middleware=mw, n_worker=None)

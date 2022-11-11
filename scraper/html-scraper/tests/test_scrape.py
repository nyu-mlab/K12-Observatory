import http.server
import errno
import itertools
import weakref
import socket
import urllib.parse
import pathlib
import mimetypes
import re
import os
import threading
import pytest
import requests

try:
    import mock
except ModuleNotFoundError:
    from utils import mock


class Url:
    """Custom URL expression from HTTPServer and resource path"""
    servers = weakref.WeakValueDictionary()

    def __init__(self, server_name: str, path: str):
        self.server_name = server_name
        self.path = urllib.parse.quote(path)

    def __str__(self):
        """Runtime server lookup and URL generation"""
        server = self.servers[self.server_name]
        assert server.address_family in (socket.AF_INET, socket.AF_INET6)
        return f"http://localhost:{server.server_address[1]}/{self.path}"


def build_html(path: str, links: list[Url]) -> str:
    return mock.template.render(
        title=path,
        links=(dict(href=str(link), caption=str(link)) for link in links),
    )


def handler_factory(handler_dict: dict[str, Url]):
    # TODO: give more responses, such as certain paths that trigger different responses and status codes, to test the scraper under different conditions (how to react when the status is 2/3/4/5XX)
    # NOTE: if we are implementing various responses, we might as well replace the built-in http module with a serious server, maybe Flask or Tornado? want it to be as lightweight as possible though
    def request_handler(self):
        path = self.path.lstrip("/")
        print("got request:", path)

        static_resource_dir = pathlib.Path(mock.__file__).parent / "static"
        if (static_file := static_resource_dir / path).is_file():
            self.send_response(200)
            self.send_header("Content-type", mimetypes.guess_type(path))
            self.end_headers()
            self.wfile.write(static_file.read_bytes())

        elif path in handler_dict:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write((build_html(path, handler_dict[path])).encode())

        else:
            self.send_error(404)

    return request_handler


@pytest.fixture
def http_server():
    # TODO: let fixture inspect the requesting test context and decide whether to use TTL or not

    def _http_server(pages):
        for port in itertools.chain(range(8000, 9000), "X"):
            if port == "X":
                raise OSError(errno.EADDRNOTAVAIL,
                              os.strerror(errno.EADDRNOTAVAIL))

            try:
                # TODO: replace port trying and set this to port 0 instead to let the OS find a free port
                # TODO: if we were to replace this entire for-range-try-port thing with port=0, we might as well simply the structure and merge this entire function into mock_site()
                request_handler = type("HTTPRequestHandler",
                                       (http.server.BaseHTTPRequestHandler,),
                                       dict(do_GET=handler_factory(pages)))
                # HACK: exploit the fact that HTTPServer's context manager does nothing, replace "yield" with "return"
                return http.server.HTTPServer(("", port), request_handler)
                break

            except OSError as err:
                if err.errno != errno.EADDRINUSE:
                    os.strerror(err.errno)
                    raise err

    return _http_server


@pytest.fixture(scope="function")
def mock_site(request):

    def _mock_site(name: str, pages: dict[str, Url]):

        request_handler = type("HTTPRequestHandler",
                               (http.server.BaseHTTPRequestHandler,),
                               dict(do_GET=handler_factory(pages)))
        # NOTE: the context manager of HTTPServer is merely a "pass" statement, skip the "with" statement
        server = http.server.ThreadingHTTPServer(("", 0), request_handler)
        Url.servers[name] = server
        print("Serving on port:", server.server_address[1])

        # NOTE: serve_forever() checks "poll_interval", handle_request() checks "timeout"
        # NOTE: httpd.shutdown() will work after "polling_interval"
        thread = threading.Thread(target=server.serve_forever)
        thread.start()

        def stop_server():
            assert thread.is_alive()
            server.shutdown()
            server.server_close()
            thread.join(1)
            assert not thread.is_alive()

        request.addfinalizer(stop_server)
        return server

    return _mock_site


class TestMockSite:

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

        port = main_site.server_address[1]

        for i in range(1, 4):
            path = Url("main", f"page{i}")
            print(path, repr(path), str(path))
            r = requests.get(str(path), timeout=(0.1, 0.1))

            assert r.ok
            # NOTE: keep validation scheme simple
            assert re.search(fr"<title>page{i}</title>", r.text)


class TestScraping:
    pass

    # TODO: do test case setup: run_server()

    # TODO: test scraping mock server for single page, then halt and inspect
    def test_scrape_single_page(self, mock_site):
        # TODO: set TTL = 1
        pass

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

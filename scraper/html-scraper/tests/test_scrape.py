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
def server_ttl():
    # FIXME: TTL's time means number of requests here
    # TODO: refactor this after implementing the site map exploring test case
    return 3


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

    def test_server_reply(self, mock_site, server_ttl):
        httpd, thread = mock_site
        addr, port = httpd.server_address

        from time import sleep
        for i in range(server_ttl):
            resource_path = "".join(random.sample(string.ascii_letters, 4))
            r = requests.get(f"http://localhost:{port}/{resource_path}",
                             timeout=(0.1, 0.1))
            assert r.ok
            assert re.search(fr"\breq={resource_path}\b", r.text)
            assert re.search(r"\bTTL=\d+\b", r.text)

            # NOTE: keep validation scheme simple


class TestScraping:
    pass

    # TODO: do test case setup: run_server()

    # TODO: test scraping mock server for single page, then halt and inspect
    def test_scrape_single_page(self, mock_site):
        # TODO: set TTL = 1
        pass

    # TODO: test scraping mock server for automated-whole-site scraping, then inspect site map
    def test_scrape_site(self, mock_site):
        # TODO: turn off TTL
        pass

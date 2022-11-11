import http.server
import errno
import itertools
import random
import string
import re
import os
import threading
import pytest
import requests

try:
    import mock
except ModuleNotFoundError:
    from utils import mock

def get_handler(self):
    # TODO: give more responses, such as certain paths that trigger different responses and status codes, to test the scraper under different conditions (how to react when the status is 2/3/4/5XX)
    # NOTE: if we are implementing various responses, we might as well replace the built-in http module with a serious server, maybe Flask or Tornado? want it to be as lightweight as possible though
    """GET method request handler"""
    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write((f"req={self.path.lstrip('/')}\n"
                      f"TTL={self.TTL}").encode())
    # TODO: return normal html
    # TODO:optional: do templating?


def meta_request_handler(ttl):
    """Creates a request handler class that dies after TTL"""
    return type(
        "HTTPRequestHandler",
        (http.server.BaseHTTPRequestHandler,),
        dict(TTL=ttl, do_GET=get_handler),
    )


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
def mock_site(http_server):
    print("Serving on port:", http_server.server_address[1])

    def serve():
        # TODO: add stop mechanism for http_server.serve_forever()
        # NOTE: httpd.shutdown() will work after polling interval

        # TODO: don't just suppress error, use 'pytest.raises' or 'pytest.warns' instead for such expected errors
        try:
            http_server.serve_forever()
        except ValueError as err:
            # Suppress error if caused by force closing the server from outside
            # FIXME: might suppress other issues as well
            if err.args[0] != "Invalid file descriptor: -1":
                raise err

    http_server.timeout = 1
    thread = threading.Thread(target=serve)
    thread.start()

    yield http_server, thread

    http_server.shutdown()
    http_server.server_close()
    thread.join(http_server.timeout + 1)
    assert not thread.is_alive()


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

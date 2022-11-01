import http.server
import errno
import itertools
import os
import threading
import pytest
import requests

# TODO: Test then setup http server


def get_handler(self):
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
def http_server(server_ttl):
    # TODO: let fixture inspect the requesting test context and decide whether to use TTL or not

    for port in itertools.chain(range(8000, 9000), "X"):
        if port == "X":
            raise OSError(errno.EADDRNOTAVAIL, os.strerror(errno.EADDRNOTAVAIL))

        try:
            with http.server.HTTPServer(
                ("", port), meta_request_handler(server_ttl)) as httpd:
                yield httpd
            break

        except OSError as err:
            if err.errno != errno.EADDRINUSE:
                os.strerror(err.errno)
                raise err


@pytest.fixture(scope="function")
def mock_site(http_server, server_ttl):
    print("Serving on port:", http_server.server_address[1])

    def serve():
        # TODO: serve indefinitely for sitemap exploring test cases, maybe count TTL in the handler?
        # TODO: add stop mechanism for http_server.serve_forever()
        # NOTE: httpd.shutdown() will work after polling interval
        for i in range(server_ttl):
            try:
                http_server.handle_request()
            except ValueError as err:
                # Suppress error if caused by force closing the server from outside
                # FIXME: might suppress other issues as well
                if err.args[0] != "Invalid file descriptor: -1":
                    raise err

    http_server.timeout = 1
    thread = threading.Thread(target=serve)
    thread.start()

    yield http_server, thread

    http_server.server_close()
    thread.join(http_server.timeout + 1)
    assert not thread.is_alive()


class TestMockSite:

    def test_server_reply(self, mock_site, server_ttl):
        httpd, thread = mock_site
        addr, port = httpd.server_address

        from time import sleep
        for i in range(server_ttl):
            requests.get(f"http://localhost:{port}/aa", timeout=(0.1, 0.1))
            # TODO: inspect reply, grep for certain path or TTL for validation (should be enough)


class TestScraping:
    pass

    # TODO: do test case setup: run_server()

    # TODO: test scraping mock server for single page, then halt and inspect
    def test_scrape_single_page(self, mock_site):
        # TODO: set TTL = 1
        pass

    # TODO: test scraping mock server for automated-whole-site scraping, then inspect site map

"""Utilities
"""
import http.server
import mimetypes
import pathlib
import socket
import threading
import urllib
import weakref

import jinja2
import jinja2.sandbox
import pytest

env = jinja2.sandbox.SandboxedEnvironment(
    loader=jinja2.FileSystemLoader(
        pathlib.PurePath(__file__).parent / "template"),
    autoescape=jinja2.select_autoescape,
)
template = env.get_template("index.jinja")


class Url:
    """Custom URL expression from HTTPServer and resource path"""
    servers: weakref.WeakValueDictionary[
        str, http.server.HTTPServer |
        http.server.ThreadingHTTPServer] = weakref.WeakValueDictionary()

    def __init__(self, server_name: str, path: str):
        self.server_name = server_name
        self.path = urllib.parse.quote(path)

    def __str__(self):
        """Runtime server lookup and URL generation"""
        server = self.servers[self.server_name]
        assert server.address_family in (socket.AF_INET, socket.AF_INET6)
        return f"http://localhost:{server.server_address[1]}/{self.path}"


def build_html(path: str, links: list[Url]) -> str:
    return template.render(
        title=path,
        links=(dict(href=str(link), caption=str(link)) for link in links),
    )


def handler_factory(handler_dict: dict[str, Url]):
    # TODO: give more responses, such as certain paths that trigger different responses and status codes, to test the scraper under different conditions (how to react when the status is 2/3/4/5XX)
    # TODO: if we are implementing various responses, we might as well replace the built-in http module with a serious server, maybe Flask or Tornado? want it to be as lightweight as possible though
    def request_handler(self):
        path = self.path.lstrip("/")
        print("got request:", path)

        static_resource_dir = pathlib.Path(__file__).parent / "static"
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


@pytest.fixture(scope="function")
def site_generator(request):

    def _site(name: str, pages: dict[str, Url]):

        request_handler = type("HTTPRequestHandler",
                               (http.server.BaseHTTPRequestHandler,),
                               dict(do_GET=handler_factory(pages)))
        # TODO: HTTPServer or ThreadingHTTPServer? prefer HTTPServer if possible
        # NOTE: the context manager of HTTPServer is merely a "pass" statement, skip the "with" statement
        server = http.server.HTTPServer(("", 0), request_handler)
        Url.servers[name] = server
        print("Serving on port:", server.server_address[1])

        thread = threading.Thread(target=server.serve_forever,
                                  kwargs=dict(poll_interval=0.1))
        thread.start()

        def stop_server():
            assert thread.is_alive()
            server.shutdown()
            server.server_close()
            # NOTE: serve_forever() default "poll_interval" is 0.5 sec
            thread.join(0.2)
            assert not thread.is_alive()

        request.addfinalizer(stop_server)
        return server

    return _site


__all__ = [
    "Url",
    "site_generator",
]

if __name__ == "__main__":
    print(
        template.render(title="king of the north",
                        links=[dict(href="aaa", caption="bbb")]))

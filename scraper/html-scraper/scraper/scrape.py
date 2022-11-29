""" Main scraper code
"""
import functools
import importlib.resources
import itertools
import random
import requests
import scraper


class Task:
    # TODO: record self.response.elapsed info for scheduling

    class Request:

        def __init__(
            self,
            request: requests.Request,
            timeout,
            priority,
        ):
            self.request = request
            self.timeout = timeout
            self.priority = priority  # additional priority for scheduler to use (e.g. can be used to crawl shallow pages first or deep pages first)
            # TODO: consider doing "request-fingerprinting" to filter out duplicate requests or cache them
        # TODO: log timestamp before sending

    def __init__(
        self,
        request: requests.Request,
        *,
        timeout=60,
        priority=1,
        #referer=None, # TODO: move this to a middleware and log it in self.metadata
        #root_request_hostname=None,  # TODO: move this to DropSecondLevelThirdPartyMiddleware and log it in self.metadata
    ):
        self.request = self.Request(request, timeout, priority)
        self.response = None
        self.metadata = {}

        # TODO: in some middleware: if is root request (no previous value set), set depth=1, root_hostname=hostname



class StartURLs:

    def __init__(self, *argv, shuffle=False, random_seed=None):
        """argv is a list of list of URLs,
        e.g.
        StartURLs(
            [
                "aaa",
                "bbb",
            ],
            [
                "ccc",
                "ddd",
            ],
        )
        """
        self.urls = set(itertools.chain(*argv))

        if shuffle:
            random.seed(random_seed)
            self.urls = list(self.urls)
            random.shuffle(self.urls)

    def __iter__(self):
        return iter(self.urls)

    def __repr__(self) -> str:
        return repr(self.urls)


class Scraper:

    def __init__(self, start_urls: StartURLs, *args, **kwargs):
        pass


def scrape():

    Scraper(
        StartURLs(
            scraper.target.extract(
                data_dir=importlib.resources.files(scraper.targets),
                usecols=["Website"],
                dtype={"Website": "string"},
            )),
        scraper.Crawler(),
        scraper.Downloader(),
    )

    # TODO: move these to performance profiling code
    """
    fmt_str = lambda action_name: action_name + ":\n\t{:0.4f} seconds"

    Timer = scraper.perf.Timer
    with Timer(fmt_str("Read nces")):
        nces_df = pd.read_excel(nces_file)
    with Timer(fmt_str("Read k12")):
        k12_df = pd.read_csv(k12_file)

    district_url_set = set()
    with Timer(fmt_str("nces set add")):
        district_url_set |= set(nces_df["Website"])
    with Timer(fmt_str("k12 set add")):
        district_url_set |= set(k12_df["Website"])

    print(f"{'-' * 12}")
    print(f"number of targets: {len(district_url_set)}")
    """


if __name__ == "__main__":
    scrape()

""" Main scraper code
"""
import functools
import importlib.resources

import scraper


class Scraper:

    def __init__(
        self,
        start_urls: scraper.target.StartURLs,
        crawler: scraper.Crawler,
        downloader: scraper.Downloader,
        scheduler,
        *args,
        **kwargs,
    ):

        # Piping scheduler, downloader, and crawler
        crawler.input_queue = downloader.output_queue
        scheduler.input_queue = crawler.output_queue

        self.crawler = crawler
        self.downloader = downloader
        self.scheduler = scheduler

        for url in start_urls:
            self.scheduler.process(url)


def scrape():

    Scraper(
        scraper.target.StartURLs(
            scraper.target.extract(
                data_dir=importlib.resources.files(scraper.targets),
                usecols=["Website"],
                dtype={"Website": "string"},
                # FIXME: nrows=2 for testing purpose
                nrows=2,
            )),
        crawler=scraper.Crawler(
            # FIXME: n_worker=1 for testing purpose
            n_worker=1,
            middleware=scraper.crawler.default_middleware,
        ),
        downloader=scraper.Downloader(
            # FIXME: n_worker=1 for testing purpose
            n_worker=1,
            middleware=scraper.downloader.default_middleware,
        ),
        scheduler=None,  # FIXME:
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

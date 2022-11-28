""" Main scraper code
"""
import importlib.resources
import itertools
import random
from scraper.perf import Timer
import scraper


class StartURLs:

    def __init__(self, *argv):
        self.urls = set(itertools.chain(*argv))

    def __iter__(self):
        return iter(self.urls)

    def __repr__(self) -> str:
        return repr(self.urls)


def scrape():

    StartURLs(
        scraper.target.extract(
            data_dir=importlib.resources.files(scraper.targets),
            usecols=["Website"],
            dtype={"Website": "string"},
        ))
    exit()

    # TODO: move these to performance profiling code
    fmt_str = lambda action_name: action_name + ":\n\t{:0.4f} seconds"

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


if __name__ == "__main__":
    scrape()

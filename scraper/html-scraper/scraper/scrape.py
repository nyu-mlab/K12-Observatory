""" Main scraper code
"""
import itertools
import importlib.resources
import pandas as pd
import scraper
from scraper.perf import Timer

valid_extensions = {
    # maps extension to pandas opening function name suffix
    "csv": "csv",
    "xlsx": "excel",
}


class StartURLs:

    def __init__(self, *argv):
        self.urls = set(itertools.chain(*argv))

    def __iter__(self):
        return iter(self.urls)


def get_targets():
    """locate resources and find a way to open them"""

    assert (data_dir := importlib.resources.files(scraper.targets)).is_dir()

    file_method_mapping = {
        file: getattr(pd, "read_" + valid_extensions[file.suffix.lstrip(".")])
        for file in data_dir.iterdir()
        if file.is_file() and file.suffix.lstrip(".") in valid_extensions
    }
    return file_method_mapping


def scrape():

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

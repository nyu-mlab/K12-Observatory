""" Main scraper code
"""
import importlib.resources
import pandas as pd
import scraper
from scraper.perf import Timer

valid_extensions = {
    "csv",
    "xlsx",
}


def get_targets():
    """locate resources and find a way to open them"""
    assert (data_dir := importlib.resources.files(scraper.targets)).is_dir()

    return (file for file in data_dir.iterdir()
            if file.is_file() and file.suffix.lstrip(".") in valid_extensions)


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

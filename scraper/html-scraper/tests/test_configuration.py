import itertools
import importlib.resources
import scraper


class TestTargetAcquisition:

    def test_found_all_targets(self):
        valid_extensions = (
            "csv",
            "xlsx",
        )

        assert (data_dir := importlib.resources.files(scraper.targets)).is_dir()

        valid_files = list(
            itertools.chain.from_iterable(
                data_path.glob(f"**/*.{extension}")
                for extension in valid_extensions
                for data_path in data_dir._paths))

        assert set(scraper.scrape.get_targets()) == set(valid_files)

        print([f.name for f in valid_files])
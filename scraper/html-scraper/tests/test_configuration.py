import itertools
import importlib.resources
import pandas as pd
import scraper


@pytest.fixture
def data_dir():
    assert (datadir := importlib.resources.files(scraper.targets)).is_dir()
    return datadir


class TestTargetAcquisition:

    def test_file_open_method_mapping(self):
        """Confirm that file extensions are mapped to valid function names"""
        assert all(
            map(lambda x: hasattr(pd, x) and callable(getattr(pd, x)), (
                "read_" + n for n in scraper.scrape.valid_extensions.values())))

    def test_find_all_targets(self, data_dir):
        # TODO: add test that generates fake files with valid and invalid extensions in a temp dir to further test target-finding

        valid_files = list(
            itertools.chain.from_iterable(
                data_path.glob(f"**/*.{extension}")
                for extension in scraper.scrape.valid_extensions
                for data_path in data_dir._paths))

        assert set(scraper.scrape.get_targets()) == set(valid_files)

        print([f.name for f in valid_files])

    def test_files_mapped_to_correct_open_func(self, data_dir):
        # TODO: this takes too long, consider building fake files in a temp dir or mark this test as slow to allow skipping

        for path, func in scraper.scrape.get_targets().items():
            # asserts no exception
            func(path)

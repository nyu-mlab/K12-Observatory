import importlib.resources
import itertools
import pandas as pd
import pytest
import scraper


@pytest.fixture
def data_dir():
    assert (datadir := importlib.resources.files(scraper.targets)).is_dir()
    return datadir


class TestTargetAcquisition:

    def test_file_open_method_mapping(self):
        """Confirm that file extensions are mapped to valid function names"""
        assert all(
            map(lambda x: hasattr(pd, x) and callable(getattr(pd, x)),
                ("read_" + n for n in scraper.target.TargetAcquisitionHelper.
                 valid_extensions.values())))

    def test_find_targets(self, data_dir):
        # TODO: add test that generates fake files with valid and invalid extensions in a temp dir to further test target-finding

        valid_files = set(
            itertools.chain.from_iterable(
                data_path.glob(f"**/*.{extension}")
                for extension in
                scraper.target.TargetAcquisitionHelper.valid_extensions
                for data_path in data_dir._paths))

        extracted_files = scraper.target.extract.find(data_dir)
        found_files = set(itertools.chain(extracted_files.keys()))

        assert found_files == valid_files

        print(f"valid_files: ({len(valid_files)} ",
              *(f.name for f in valid_files))
        print(f"found_files: ({len(found_files)} ",
              *(f.name for f in found_files))

    def test_files_mapped_to_correct_open_func(self, data_dir):
        # TODO: this takes too long, consider building fake files in a temp dir or mark this test as slow to allow skipping

        # NOTE: asserts no exception
        scraper.target.extract(
            data_dir=data_dir,
            usecols=["Website"],
            dtype={"Website": "string"},
            nrows=5,
        )


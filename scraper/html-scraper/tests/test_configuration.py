import importlib.resources
import itertools
import math

import pandas as pd
import pytest

import scraper


@pytest.fixture
def data_dir():
    assert (datadir := importlib.resources.files(scraper.targets)).is_dir()
    # NOTE: data_dir fixture returns a "importlib.resources.abc.Traversable" instance, not "pathlib.Path", consider casting its member "._paths" path list to pathlib types
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
            nrows=5,
        )
        scraper.target.extract(
            data_dir=data_dir,
            usecols=["Website"],
            dtype={"Website": "string"},
            nrows=5,
        )


@pytest.fixture(scope="session")
def random_str_group():
    return tuple(
        tuple("".join(p)
              for p in itertools.permutations(substring))
        for substring in ("AB", "CD"))


class TestStartUrlAssembly:

    def test_concat_multiple_lists(self):
        expected_url_set = {"aaa", "bbb", "ccc", "ddd"}
        result = scraper.target.StartURLs(["aaa", "bbb"], ["ccc", "ddd"]).urls
        assert expected_url_set == result
        assert expected_url_set == result

    def test_concat_list_of_lists(self, random_str_group):
        fixture_ans = set(itertools.chain.from_iterable(random_str_group))
        result = scraper.target.StartURLs(*random_str_group).urls
        assert fixture_ans == set(result)
        assert fixture_ans == result

    def test_concat_real_data(self, data_dir):
        # FIXME: STILL TAKES TOO LONG TO EXECUTE
        """test normal usage"""
        # example setup
        start_urls = scraper.target.StartURLs(
            scraper.target.extract(
                data_dir=data_dir,
                usecols=["Website"],
                dtype={"Website": "string"},
                nrows=2,
            )).urls
        assert isinstance(start_urls, set)
        assert len(start_urls) > 0
        assert isinstance(list(start_urls)[0], str)

    @pytest.mark.xfail(True,
                       raises=RuntimeError,
                       reason="randomization makes it flaky",
                       strict=False)
    def test_shuffle(self, random_str_group):
        # TODO: replace with 'hypothisis' library
        string_list = list(itertools.chain.from_iterable(random_str_group))

        # NOTE: The possibility of the shuffled list maintaining its original
        # order makes this a flaky test, but configuring a static random seed
        # for repeatability breaks other libraries, e.g. OpenTelemetry random
        # ID generator, so we repeat the test to keep false positive rate below
        # $TARGET_FALSE_POSITIVE_RATE
        TARGET_FALSE_POSITIVE_RATE = 1E-4
        chance_of_original_order = 1 / len(string_list)  # per one shuffle

        # Probability of getting at least one successful shuffle (order did
        # change) after X shuffles = 1 - (chance_of_original_order ** X),
        # essentially keeping (chance_of_original_order ** X) smaller or equal
        # to $TARGET_FALSE_POSITIVE_RATE

        def successful_shuffle(dummy_arg):
            # Order did change
            random_result = scraper.target.StartURLs(*random_str_group,
                                                     shuffle=True,
                                                     random_seed=None).urls
            assert len(string_list) == len(random_result)
            assert set(string_list) == set(random_result)

            return string_list != random_result

        if not any(
                map(
                    successful_shuffle,
                    range(
                        min(
                            1,
                            len(string_list) * 100,
                            math.ceil(
                                math.log(TARGET_FALSE_POSITIVE_RATE,
                                         chance_of_original_order)),
                        )),
                )):
            raise RuntimeError()

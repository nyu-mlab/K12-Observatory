"""Target acquisition
"""
import itertools
import random

import pandas as pd


class StartURLs:
    """Lists of URLs to start from.
    """

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


class TargetAcquisitionHelper:
    """helper function to get root URLs"""

    valid_extensions = {
        # maps extension to pandas opening function name suffix
        "csv": "csv",
        "xlsx": "excel",
    }

    @classmethod
    def find(cls, data_dir):
        """locate resources and find a way to open them"""
        assert data_dir.is_dir()
        file_method_mapping = {
            file:
            getattr(pd, "read_" + cls.valid_extensions[file.suffix.lstrip(".")])
            for file in data_dir.iterdir()
            if file.is_file() and
            file.suffix.lstrip(".") in cls.valid_extensions
        }
        return file_method_mapping

    def __call__(self, *, data_dir, **kwargs):
        """actually opening resources

            carries Pandas file reading arguments:
            - usecols : list[str] (mandatory)
            - dtype : dict[str, str] (optional)
        """
        usecols = kwargs["usecols"]
        assert len(usecols) == 1
        if dtype := kwargs.get("dtype"):
            assert set(dtype.keys()) == set(usecols)

        extracted = itertools.chain.from_iterable(
            method(file, **kwargs).squeeze("columns").to_list()
            for file, method in self.find(data_dir).items())

        return extracted


extract = TargetAcquisitionHelper()

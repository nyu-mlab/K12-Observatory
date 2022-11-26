"""Target acquisition"""

import pandas as pd


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
        """actually opening resources"""
        extracted = [
            method(file, **kwargs)
            for file, method in self.find(data_dir).items()
        ]
        return extracted


extract = TargetAcquisitionHelper()

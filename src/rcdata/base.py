"""
Common base class for all data
"""

import os
import json
from pathlib import Path

from typing import Any


class BaseData:
    """
    Common base class for all data
    """

    def __init__(self, defaults: dict):
        object.__setattr__(self, "_defaults", defaults)  # 默认值，不能修改
        self._data = {}  # 实际数据

    def __getattr__(self, name):
        """
        Args:
            name: str, the key name to be found.
        Look in __dict__; if not found, then check _data and _defaults.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self._data:
            return self._data[name]
        if name in self._defaults:
            return self._defaults[name]

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value: Any):
        """
        Args:
            name: str, the key name to be set.
            value: Any, the value to be set.
        Check if the specified key name exists in the _defaults dictionary.
        If the key exists, write the value value into the _data dictionary.
        When the key does not exist, directly set the object's attribute using object.__setattr__.
        """
        if name in self._defaults:
            self._data[name] = value
        else:
            object.__setattr__(self, name, value)

    @staticmethod
    def mkdir(path: str) -> int:
        """
        Args:
            file_path (str): file path

        Returns:
            int: status
                - 0: success
                - 11: directory exists
                - 20: failed to create directory
        """
        dir_path = Path(path).parent
        if path.isdir(path):
            return 11
        try:
            os.makedirs(dir_path)
        except Exception:  # pylint: disable=broad-exception-caught
            return 20
        return 0

    def load(self, path: str, compact: bool = False) -> dict:
        """
        Load data from a file.

        Args:
            path (str): file path

        Returns:
            dict: data
        """
        if not compact:
            with open(path, "r", encoding="utf-8") as file:
                self._data = json.load(file)
        else:
            from zstandard import ZstdDecompressor
            with open(path, 'rb') as file:
                self._data = json.loads(ZstdDecompressor().\
                    decompress(file.read()).decode('utf-8'))

    def sync(self, path, compact: bool = False):
        """
        Sync data to a file.
        """
        if not compact:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(self._data, file)
        else:
            from zstandard import ZstdCompressor
            with open(path, 'wb') as file:
                file.write(ZstdCompressor().\
                    compress(json.dumps(self._data).encode('utf-8')))  # 压缩并写入文件

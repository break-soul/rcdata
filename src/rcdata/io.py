"""
Common io function for all data
"""

import os
import json
from pathlib import Path
from functools import lru_cache


@lru_cache(4)
def get_zstd(i: int = 0):
    """
    0 is for compress, 1 is for decompress, other is invalid
    """
    try:
        if i == 0:
            from zstandard import ZstdCompressor as zstd
        elif i == 1:
            from zstandard import ZstdDecompressor as zstd
        else:
            raise ValueError("Invalid i")
    except ImportError:
        raise ImportError("You need to install zstandard to use this function")
    return zstd


@lru_cache(4)
def get_encrypt(i: int = 0): ...


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


def load(path: str, compact: bool = False, encrypt: bool = False) -> dict:
    """
    Load data from a file.

    Args:
        path (str): file path

    Returns:
        dict: data
    """
    if not compact:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        with open(path, "rb") as file:
            return json.loads(get_zstd(1).decompress(file.read()).decode("utf-8"))


def sync(data: dict, path: str, compact: bool = False, encrypt: bool = False):
    """
    Sync data to a file.
    """
    if not compact:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)
    else:
        with open(path, "wb") as file:
            file.write(
                get_zstd(0).compress(json.dumps(data).encode("utf-8"))
            )  # 压缩并写入文件

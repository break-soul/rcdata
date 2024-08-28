import os
from typing import Union, Tuple
from .base import BaseData, Field


def get_file_extension(file_path: str) -> Tuple[str, str]:
    return os.path.splitext(file_path)


class Resource(BaseData):
    """The `Resource` class is a subclass of `BaseData` and is used to represent a resource file."""

    name = Field("", str)

    def __init__(
        self, path: str, /, encrypt: bool = False, **kw
    ) -> None:
        _, extension = get_file_extension(path)
        if extension == ".resource":
            compact = False
        elif extension == ".cresource":
            compact = True
        if encrypt:
            self.key = kw.pop("key")
        super().__init__(
            path=path,
            data_type=b"\x00\x01\x00",
            init_p=-1,
            env_p=-1,
            default_p=-1,
            compact=compact,
            encrypt=encrypt,
            key=self.key,
            **kw,
        )


class ResourceIndex(BaseData):
    """The `ResourceIndex` class is a subclass of `BaseData` and is used to index resource file."""

    file_list = Field([], list)
    file_hash = Field({}, dict)

    def __init__(self, path: str | None = None, key: str = None, /, **kw) -> None:
        self.root, extension = get_file_extension(path)
        self.key = key
        if extension == ".index":
            compact = False
        elif extension == ".cindex":
            compact = True
        super().__init__(
            path=path,
            data_type=b"\x00\x01\x01",
            init_p=-1,
            env_p=-1,
            compact=compact,
            encrypt=False,
            **kw,
        )
        self.res_dict = dict()
        self.load_res()

    def load_res(self) -> None:
        if self.key is not None:
            encrypt = True
        for file in self.file_list:
            try:
                path = os.path.join(self.root, file)
                res = Resource(path=path, encrypt=encrypt, key=self.key)
                self.res_dict[file] = res
            except Exception:
                pass

    def get_res(self, res: str) -> str:
        return self.res_dict[res]

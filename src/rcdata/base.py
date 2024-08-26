"""
Common base class for all data
"""

import os

from typing import Any, Union, List, overload

from .io import load, sync


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


class Field:
    __slots__ = ("default", "type", "data", "name")

    _FIELD = "Field"

    def __init__(
        self,
        default: Any = MISSING,
        default_type: Any = MISSING,
    ) -> None:
        if default is MISSING and default_type is MISSING:
            raise ValueError("default or default_type must be provided")
        if default is not MISSING and default_type is not MISSING:
            if self.check_type(default, default_type):
                self.default = default
                self.type = default_type
            else:
                raise ValueError("default value does not match the type")
        else:
            if default is not MISSING:
                self.type = type(default)
            else:
                self.type = default_type
            self.default = default
        self.data = default

    # region check_type
    @overload
    def check_type(self) -> bool: ...
    @overload
    def check_type(self, value: Any) -> bool: ...
    @overload
    def check_type(self, value: Any, type_: type) -> bool: ...
    def check_type(self, value: Any = MISSING, type_: type = MISSING) -> bool:
        if value is MISSING:
            return isinstance(self.data, self.type)
        if type_ is MISSING:
            return isinstance(value, self.type)
        return isinstance(value, type_)

    # endregion

    def __repr__(self) -> str:
        return f"{self._FIELD}(default={self.default}, type={self.type})"

    def set_name(self, name: str) -> None:
        self.name = name

    def set_data(self, data: Any) -> None:
        if self.check_type(data):
            self.data = data
        else:
            raise ValueError("data does not match the type")

    def __set_name__(self, owner, name):
        func = getattr(type(self.default), "__set_name__", None)
        if func:
            func(self.default, owner, name)


class BaseData:
    """
    Common base class for all data

    attr = Field(default,type,**kw)
    """

    def __new__(cls) -> "BaseData":
        fields = dict()
        for _name, _field in cls.__dict__.items():
            if getattr(_field, "_FIELD", None) is not None:
                _field.set_name(_name)
                fields[_name] = _field
        obj = super().__new__(cls)
        obj._fields = fields
        return obj

    def __init__(
        self,
        /,
        path: Union[str, None] = None,
        init_p: int = 4,
        env_p: int = 3,
        file_p: int = 2,
        default_p: int = 1,
        compact: bool = False,
        encrypt: bool = False,
        data_type: bytes = b"\x00\x00\x00",
        hash_type: bool = False,
        **kw,
    ) -> None:
        """
        Args:
            path (Union[str, None], optional): path to the data file. Defaults to None.
        # priority of data, higher priority will overwrite lower priority, -1 to disable
            init_p (int, optional): priority of init data. Defaults to 4.
            env_p (int, optional): priority of env data. Defaults to 3.
            file_p (int, optional): priority of file data. Defaults to 2.
            default_p (int, optional): priority of default data. Defaults to 1.
        # data processing
            compact (bool, optional): compact the data. Defaults to False.
                if compact is True, will find compact_type in the kw, and use the compact_type to compact the data.
            compact_type (str, optional): compact type. Defaults to "zstd".
            encrypt (bool, optional): encrypt the data. Defaults to False.
                if encrypt is True, will find encrypt_type in the kw, and use the encrypt_type to encrypt the data.
            encrypt_type (str, optional): encrypt type. Defaults to "edrsa".
            key (str, optional): key for encrypt. Defaults to None.
            data_type (bytes, optional): data type. Defaults to b"\x00\x00\x00".
            hash_type (bool, optional): hash the data. Defaults to False.
                if hash is True, will find hash_type in the kw, and use the hash_type to hash the data.
            hash_type (str, optional): hash type. Defaults to "sha256".
            prime (bytes, optional): prime number. Defaults to 0b111.
                only used by encrypted data.First byte is for creator, second byte is for encrypt, third byte is for any.
                if 111 the encrypt will not use!
        """
        self._path = path
        self._compact = compact
        self._encrypt = encrypt
        self._data_type = data_type
        self._hash = hash_type
        self._p = {
            init_p: self._load_init,
            env_p: self._load_env,
            file_p: self._load_file,
            default_p: self._load_default,
        }
        self._kw = kw
        self._dump_config()
        self._load_data()

    def _dump_config(self) -> None:
        self._mate = {
            "version": 0,
            "compact": self._compact,
            "encrypt": self._encrypt,
            "type": self._data_type,
            "hash": self._hash,
        }
        if self._compact:
            self._compact_type = self._kw.pop("compact_type", "zstd")
            self._mate["compact_type"] = self._compact_type
        if self._encrypt:
            self._encrypt_type = self._kw.pop("encrypt_type", "edrsa")
            self._prime = self._kw.pop("prime", 0b111)
            self._key = self._kw.pop("key", None)
            self._mate["encrypt_type"] = self._encrypt_type
            self._mate["prime"] = self._prime
        if self._hash:
            self._hash_type = self._kw.pop("hash_type", "sha256")
            self._mate["hash_type"] = self._hash_type

    def _load_data(self) -> None:
        self._p.pop(-1, None)
        for p in sorted(self._p.keys()):
            self._p[p]()
        for field in self._fields.values():
            setattr(self, field.name, field.data)

    def _load_fields(self, source: dict) -> None:
        for field in self._fields.values():
            if field.name in source:
                field.set_data(source[field.name])

    def _load_init(self):
        self._load_fields(self._kw)

    def _load_env(self):
        self._load_fields(os.environ)

    def _load_file(self):
        if self._path is not None:
            data = load(self._path, self._compact, self._encrypt).get("data")
            self._load_fields(data)

    def _load_default(self): ...  # Useless, used only as a placeholder

    def __dir__(self) -> List[str]:
        return list(self._fields.keys())

    def _write_data(self) -> dict:
        data = dict()
        for field in self._fields.values():
            data[field.name] = field.data
        self._mate["data"] = data
        return sync(self._mate, self._path, self._compact, self._encrypt)

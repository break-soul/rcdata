"""
Common base class for all data
"""

from typing import TYPE_CHECKING, Any, Union, overload


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


class Field:
    # __slots__ = ("name", "type", "default", "required")

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
        func = getattr(type(self.default),"__set_name__",None)
        if func:
            func(self.default, owner, name)


class Base:
    """
    Common base class for all data

    attr = Field(default,type,**kw)
    """

    def __new__(cls) -> "Base":
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
        **kw,
    ) -> None:
        self._path = path
        self._p = {init_p: self._load_init, env_p: self._load_env, file_p: self._load_file, default_p: self._load_default}
        self._kw = kw
        self._load_data(**kw)

    def _load_data(self, **kw) -> None:
        _p = list(self._p.keys())
        _p.sort(reverse=False)
        for p in _p:
            self._p[p]()
        for field in self._fields.values():
            self.__setattr__(field.name, field.data)

                
    def _load_init(self):...
    def _load_env(self):...
    def _load_file(self):...
    def _load_default(self):...

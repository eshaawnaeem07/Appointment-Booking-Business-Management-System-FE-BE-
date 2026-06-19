from enum import Enum as PythonEnum

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class EnumValueType(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return self._normalize(value).value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._normalize(value)

    def _normalize(self, value):
        if isinstance(value, self.enum_class):
            return value

        text = str(value)
        for item in self.enum_class:
            if text == item.value or text == item.name:
                return item

        raise ValueError(f"{text!r} is not a valid {self.enum_class.__name__}")

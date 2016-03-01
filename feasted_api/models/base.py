import json
import uuid
from typing import TypeVar, Optional

T = TypeVar('T')


class BaseValue:
    value = None
    storage_type = None

    def __init__(self, value):
        self.validate(value)
        self.value = value

    @classmethod
    def validate(cls, value):
        if not isinstance(value, cls.storage_type):
            raise ValueError(value, "is not a", cls.storage_type.__class__)

    def to_serializable(self):
        return self.value


class BaseModel:
    fields = {}
    id_field = None
    values = {}

    def __init__(self, **field_values):
        self.__class__.validate(**field_values)
        for field, value in self.fields.items():
            candidate_value = field_values.get(field)
            if isinstance(value, list):
                try:
                    value = value[0]
                    self.values[field] = [value(cand) for cand in candidate_value]
                except (IndexError, TypeError):
                    raise ValueError('malformed model list defintion or call')
            else:
                self.values[field] = value(candidate_value)

    @classmethod
    def validate(cls, **field_values):
        for field, value in field_values.items():
            field_type = cls.fields.get(field, None)
            if field_type:
                field_type.validate(value)

    @classmethod
    def from_json(cls: T, string) -> Optional[T]:
        try:
            dictionary = json.loads(string)
            new_model = cls(**dictionary)
            return new_model
        except (json.JSONDecodeError, ValueError):
            return None

    def to_serializable(self):
        dictionary = {}
        for field, value in self.values.items():
            dictionary[field] = value.to_serializable()
        return dictionary


class BaseCollectionModel:
    pass


class BooleanValue(BaseValue):
    storage_type = bool


class StringValue(BaseValue):
    storage_type = str


class IntegerValue(BaseValue):
    storage_type = int


class DateTimeValue(BaseValue):
    def to_serializable(self):
        pass

    @classmethod
    def validate(cls, value):
        pass


class URLValue(BaseValue):
    @classmethod
    def validate(cls, value):
        pass

    def to_serializable(self):
        pass


class PriceValue(BaseValue):
    storage_type = str

    @classmethod
    def validate(cls, value):
        # Check if it's a string
        super().validate(value)

        # Check if the value is numeric. Note: str.isnumeric and str.isdecimal don't seem to work
        float(value)

        # Ensure only 2 decimal places exist and exactly 1 decimal exists
        halves = value.split('.')
        if len(halves) != 2 or len(halves[1]) != 2:
            raise ValueError(value, 'is not a valid price')


class UUIDValue(BaseValue):
    def __init__(self, value):
        self.validate(value)
        # We only get to this line if value is a string because of validate
        self.value = uuid.UUID(value)

    def to_serializable(self):
        return str(self.value)

    @classmethod
    def validate(cls, value):
        # Force the value into a string for UUID parsing
        # UUID will ValueError if it's not valid
        uuid.UUID(str(value))

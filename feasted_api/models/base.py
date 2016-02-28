import json
from typing import Dict, TypeVar, Optional

T = TypeVar('T')


class BaseModel:
    required_fields = frozenset()

    def __init__(self, **kwargs: Dict):
        # Check that required fields exist
        BaseModel.validate(self.required_fields, kwargs)

        # Set all of the keys in this object to the same values of the keys in init
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __iter__(self):
        for key in self.required_fields:
            yield (key, self.__dict__[key])

    @classmethod
    def from_json(cls: T, string) -> Optional[T]:
        try:
            dictionary = json.loads(string)
            new_model = cls(**dictionary)
            return new_model
        except (json.JSONDecodeError, ValueError):
            return None

    @staticmethod
    def validate(required_fields, field_values: Dict):
        candidate = frozenset(field_values.keys())

        # Check if field values is missing required fields
        missing_required = required_fields - candidate
        if missing_required != frozenset():
            raise ValueError('Missing required fields: ',
                             ' '.join(field for field in missing_required))


class CollectionModel:
    pass

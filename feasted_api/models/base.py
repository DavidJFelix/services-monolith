import json
from typing import TypeVar

T = TypeVar('T')


class BaseModel:
    fields = {}
    id_field = None
    table = None
    values = {}

    def __init__(self, **field_values):
        for field in self.fields:
            candidate_value = field_values.get(field)
            if candidate_value is not None:
                self.values[field] = candidate_value

    @property
    def model_id(self):
        return self.fields.get(self.id_field, None)

    @classmethod
    def from_json(cls: T, string) -> T:
        try:
            dictionary = json.loads(string)
            return cls(**dictionary)
        except (json.JSONDecodeError, ValueError):
            return cls()

    def to_serializable(self):
        dictionary = {}
        for field, value in self.values.items():
            dictionary[field] = value.to_serializable()
        return dictionary

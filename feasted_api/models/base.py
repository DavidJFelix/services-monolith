import json
from typing import TypeVar, Optional

T = TypeVar('T')


class BaseModel:
    fields = ()
    id_field = ''
    table = ''
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
    def from_json(cls: T, string) -> Optional[T]:
        try:
            dictionary = json.loads(string)
            return cls(**dictionary)
        except (json.JSONDecodeError, ValueError):
            return None

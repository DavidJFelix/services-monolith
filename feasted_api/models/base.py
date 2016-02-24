from typing import Dict


class BaseModel:
    required_fields = frozenset()

    def __init__(self, **kwargs: Dict):
        BaseModel.validate(self.required_fields, kwargs)

    @staticmethod
    def validate(required_fields, field_values: Dict):
        candidate = frozenset(field_values.keys())

        # Check if field values is missing required fields
        missing_required = required_fields - candidate
        if missing_required != frozenset():
            raise ValueError('Missing required fields: ',
                             ' '.join(field for field in missing_required))

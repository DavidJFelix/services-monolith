from .allergen import Allergen
from .base import (
    BaseCollectionModel,
    BaseModel,
    BooleanValue,
    DateTimeValue,
    IntegerValue,
    PriceValue,
    StringValue,
    URLValue,
    UUIDValue,
)
from .ingredient import Ingredient
from .location import Location
from .rethinkdb import (
    RethinkCollectionMixin,
    RethinkLocationMixin,
    RethinkSingleMixin,
)


class Meal(BaseModel, RethinkSingleMixin):
    fields = {
        'meal_id': UUIDValue,
        'name': StringValue,
        'description': StringValue,
        'portions': IntegerValue,
        'portions_available': IntegerValue,
        'price': PriceValue,
        'location': Location,
        'available_from': DateTimeValue,
        'available_to': DateTimeValue,
        'ingredients': [Ingredient],
        'allergens': [Allergen],
        'preview_image_url': URLValue,
        'images': [URLValue],
        'is_active': BooleanValue,
    }
    rethink_table = 'meals'
    id_field = 'meal_id'


class MealCollection(BaseCollectionModel, RethinkCollectionMixin, RethinkLocationMixin):
    field = 'meals'
    rethink_table = 'meals'
    location_index = 'location'
    item = Meal

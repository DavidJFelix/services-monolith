from .base import (
    BaseCollectionModel,
    BaseModel,
)


class Meal(BaseModel):
    fields = (
        'meal_id',
        'name',
        'description',
        'portions',
        'portions_available',
        'price',
        'location',
        'available_from',
        'available_to',
        'ingredients',
        'allergens',
        'preview_image_url',
        'images',
        'is_active',
    )
    rethink_table = 'meals'
    id_field = 'meal_id'


class MealCollection(BaseCollectionModel):
    field = 'meals'
    rethink_table = 'meals'
    location_index = 'location'
    item = Meal

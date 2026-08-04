from django_typesense.collections import TypesenseCollection
from django_typesense import fields

class ProductCollection(TypesenseCollection):
    # Searchable fields
    query_by_fields = 'name,description' 
    
    # Define the fields Typesense will index
    name = fields.TypesenseCharField()
    description = fields.TypesenseCharField()
    price = fields.TypesenseFloatField()
    
    # Yahan image field add karein
    image = fields.TypesenseCharField(optional=True)
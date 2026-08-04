import random
from django.core.management.base import BaseCommand
from faker import Faker
from store.models import Product, ProductVariant

fake = Faker()

class Command(BaseCommand):
    help = 'Generates 20,000 products with variants'

    def handle(self, *args, **kwargs):
        categories = ['Groceries', 'Furniture', 'Fashion', 'Footwear', 'Cosmetics']
        
        # 1. Bulk Create Products
        products_to_create = []
        for _ in range(20000):
            products_to_create.append(Product(
                name=f"{fake.company()} {fake.word().capitalize()}",
                description=fake.text(),
                price=round(random.uniform(50.0, 5000.0), 2),
                category=random.choice(categories),
                stock=random.randint(0, 100)
            ))
        
        # Batch create for performance
        created_products = Product.objects.bulk_create(products_to_create)
        
        # 2. Bulk Create Variants for each Product
        variants_to_create = []
        for p in created_products:
            # Har product ke liye 2-3 variants create karein
            for _ in range(random.randint(2, 3)):
                variants_to_create.append(ProductVariant(
                    product=p,
                    color=fake.color_name(),
                    size=random.choice(['S', 'M', 'L', 'XL', 'None']),
                    stock=random.randint(0, 50)
                ))
        
        ProductVariant.objects.bulk_create(variants_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully created 20,000 products and their variants!'))
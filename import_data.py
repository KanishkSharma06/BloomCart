import sys
import os
sys.path.append(os.getcwd())
import django
import csv

# Project settings ko load karein
# Sahi line ye honi chahiye:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloomcart_project.settings')
django.setup()

from store.models import Product

# Data import karein
with open('products.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Check karein ki uniq_id khali toh nahi hai
        if not row.get('\ufeffUniq Id'):
            continue
            
        obj, created = Product.objects.update_or_create(
            uniq_id=row['\ufeffUniq Id'],
            defaults={
                'product_title': row['Product Title'],
                'price': row['Price'],
                'product_description': row['Product Description'],
                'image_url': row['Image Url'],
                'brand': row['Brand'],
                'mrp': row['Mrp'],
                'quantity': row['Quantity']
            }
        )
print("Data imported successfully!")
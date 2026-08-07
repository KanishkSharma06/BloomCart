import os
from django.db import migrations
from django.core.management import call_command

def load_products_from_json(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    if not Product.objects.exists():
        # Root directory jahan manage.py hai
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(base_dir, 'products.json')
        if os.path.exists(json_path):
            call_command('loaddata', json_path)

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'), # Apni pichhli migration ka naam yahan likhein
    ]

    operations = [
        migrations.RunPython(load_products_from_json),
    ]
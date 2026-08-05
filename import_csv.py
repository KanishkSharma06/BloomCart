import sys
from unittest.mock import MagicMock

# Typesense ko import hone se pehle hi block/fake kar rahe hain taaki error na aaye
sys.modules['typesense'] = MagicMock()
sys.modules['typesense.exceptions'] = MagicMock()

import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloomcart_project.settings')
django.setup()

from store.models import Product

def import_flipkart_products():
    csv_file_path = 'marketing_sample_for_flipkart_com-ecommerce__20191101_20191130__15k_data.csv'
    if not os.path.exists(csv_file_path):
        csv_file_path = 'products.csv'
        if not os.path.exists(csv_file_path):
            print("Error: CSV file nahi mili!")
            return

    print("CSV file read ho rahi hai...")
    df = pd.read_csv(csv_file_path, on_bad_lines='skip', engine='python')
    print(f"Total valid rows loaded: {len(df)}")

    count = 0
    for index, row in df.iterrows():
        try:
            uniq_id = str(row.get('Uniq Id', f'prod_{index}'))
            title = str(row.get('Product Title', 'Unnamed Product'))
            
            raw_price = row.get('Price') or row.get('Mrp') or 0.0
            try:
                price = float(str(raw_price).replace('₹', '').replace(',', '').strip())
            except:
                price = 0.0

            category = str(row.get('Bb Category', 'General'))
            
            # Image URL handling: Agar pipe (|) hai toh sirf pehla wala link lo
            raw_image = str(row.get('Image Url', ''))
            if '|' in raw_image:
                image_url = raw_image.split('|')[0].strip()
            else:
                image_url = raw_image.strip()

            brand = str(row.get('Brand', ''))
            stock = 10

            Product.objects.update_or_create(
                uniq_id=uniq_id,
                defaults={
                    'product_title': title[:255],
                    'price': price,
                    'category': category[:100] if category else 'General',
                    'image_url': image_url,
                    'stock': stock,
                    'brand': brand[:100] if brand else '',
                }
            )
            count += 1
            if count % 1000 == 0:
                print(f"{count} products imported successfully...")
                
        except Exception as e:
            pass

    print(f"\nSUCCESS! Total {count} products database mein save ho gaye hain with clean image URLs!")

if __name__ == '__main__':
    import_flipkart_products()
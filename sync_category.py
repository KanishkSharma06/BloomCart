import pandas as pd
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloomcart_project.settings')
django.setup()

from store.models import Product

def update_categories():
    # Yahan apni us CSV ka naam likhein jismein saare 15 columns hain
    csv_file = 'marketing_sample_for_flipkart_com-ecommerce__20191101_20191130__15k_data.csv' 
    
    print("Reading CSV...")
    df = pd.read_csv(csv_file, on_bad_lines='skip', encoding='utf-8') 
    
    print("Updating database...")
    count = 0
    for index, row in df.iterrows():
        # 'Uniq Id' aur 'Bb Category' column ke naam wahi hone chahiye jo CSV mein hain
        Product.objects.filter(uniq_id=row['Uniq Id']).update(category=row['Bb Category'])
        count += 1
        if count % 1000 == 0:
            print(f"Updated {count} products...")
            
    print("Success! All 15,003 products updated.")

if __name__ == '__main__':
    update_categories()
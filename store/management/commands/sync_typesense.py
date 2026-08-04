from django.core.management.base import BaseCommand
from store.models import Product
from store.utils import client

class Command(BaseCommand):
    help = 'Syncs all products to Typesense Cloud'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        self.stdout.write(f"Syncing {products.count()} products to Typesense...")
        
        for p in products:
            product_data = {
                'id': str(p.uniq_id),
                'title': p.product_title,
                'price': float(p.price) if p.price else 0.0,
            }
            client.collections['products'].documents.upsert(product_data)
            
        self.stdout.write(self.style.SUCCESS('Successfully synced all products!'))
import typesense
from django.core.management.base import BaseCommand
from store.models import Product

class Command(BaseCommand):
    help = 'Indexes all Django products and images into Typesense safely'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Typesense client...")

        # Safe Client Setup
        client = typesense.Client({
            'nodes': [{'host': 'fas0pie5tckr6g2hp-1.a2.typesense.net', 'port': '443', 'protocol': 'https'}],
            'api_key': 'dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR',
            'connection_timeout_seconds': 60,
        })

        # Schema Setup including image_url
        schema = {
            'name': 'products',
            'fields': [
                {'name': 'id', 'type': 'string'},
                {'name': 'title', 'type': 'string'},
                {'name': 'description', 'type': 'string', 'optional': True},
                {'name': 'brand', 'type': 'string', 'optional': True, 'facet': True},
                {'name': 'category', 'type': 'string', 'optional': True, 'facet': True},
                {'name': 'price', 'type': 'float', 'optional': True},
                {'name': 'image_url', 'type': 'string', 'optional': True}
            ]
        }

        try:
            client.collections['products'].retrieve()
            self.stdout.write("Collection 'products' already exists. Re-indexing documents...")
        except Exception:
            self.stdout.write("Creating 'products' collection in Typesense...")
            client.collections.create(schema)

        products = Product.objects.all()
        count = products.count()
        success_count = 0

        self.stdout.write(f"Starting indexing for {count} products...")

        for product in products:
            document = {
                'id': str(product.uniq_id),
                'title': str(product.product_title or ''),
                'description': str(product.product_description or ''),
                'brand': str(product.brand or ''),
                'category': str(product.category or ''),
                'price': float(product.price) if product.price else 0.0,
                'image_url': str(product.image_url or '')  # <-- Image URL yahan properly map ho raha hai
            }

            try:
                client.collections['products'].documents.upsert(document)
                success_count += 1
            except Exception as e:
                pass

        self.stdout.write(self.style.SUCCESS(f"Successfully indexed {success_count} out of {count} products into Typesense!"))
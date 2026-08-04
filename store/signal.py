from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
import typesense

client = typesense.Client({
    'nodes': [{'host': 'fas0pie5tckr6g2hp-1.a2.typesense.net', 'port': '443', 'protocol': 'https'}],
    'api_key': 'dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR',
    'connection_timeout_seconds': 10
})

@receiver(post_save, sender=Product)
def update_typesense(sender, instance, **kwargs):
    product_data = {
        'id': str(instance.uniq_id),
        'title': instance.product_title,
        'price': float(instance.price) if instance.price else 0.0,
        'image_url': str(instance.image_url) if instance.image_url else '',
    }
    try:
        client.collections['products'].documents.upsert(product_data)
    except Exception as e:
        print(f"Typesense Sync Error: {e}")

@receiver(post_delete, sender=Product)
def delete_from_typesense(sender, instance, **kwargs):
    try:
        client.collections['products'].documents[str(instance.uniq_id)].delete()
    except:
        pass
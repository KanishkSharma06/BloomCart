from django.apps import AppConfig
import os
from django.core.management import call_command

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # 1. Database entries aur products load karne ke liye
        try:
            from django.db import connection
            # Sirf tab load karein agar table khali ho
            if 'store_product' in connection.introspection.table_names():
                from .models import Product
                if not Product.objects.exists():
                    json_path = os.path.join(os.path.dirname(__file__), '..', 'products.json')
                    if os.path.exists(json_path):
                        call_command('loaddata', json_path)
        except Exception:
            pass

        # Baaki database entries
        try:
            import store.signal
        except ImportError:
            pass

        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp
            from django.contrib.auth.models import User

            site, created = Site.objects.get_or_create(
                id=1, 
                defaults={'domain': 'bloomcart-30cs.onrender.com', 'name': 'BloomCart'}
            )
            if not created:
                site.domain = 'bloomcart-30cs.onrender.com'
                site.save()

            client_id = os.getenv('GOOGLE_CLIENT_ID', '')
            secret = os.getenv('GOOGLE_SECRET', '')
            
            if client_id and secret:
                app, app_created = SocialApp.objects.update_or_create(
                    provider='google',
                    defaults={
                        'name': 'Google',
                        'client_id': client_id,
                        'secret': secret,
                    }
                )
                if not app.sites.filter(id=site.id).exists():
                    app.sites.add(site)

            if not User.objects.filter(username='kanishk').exists():
                User.objects.create_superuser('kanishk', 'kanishkmeenakshisharma06@gmail.com', 'kanishk@13')

        except Exception:
            pass
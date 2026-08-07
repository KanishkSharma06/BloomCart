from django.apps import AppConfig
import os
from django.core.management import call_command

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Python 3.14 Context copy fix for Admin panel
        try:
            from django.template.context import Context
            def new_copy(self):
                dup = Context()
                dup.dicts = [dict(d) for d in self.dicts]
                return dup
            Context.__copy__ = new_copy
        except Exception:
            pass

        try:
            import store.signal
        except ImportError:
            pass

        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp
            from django.contrib.auth.models import User
            from django.db import connection

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

            # Exact path for products.json in main root folder (where manage.py is)
            if 'store_product' in connection.introspection.table_names():
                from .models import Product
                if not Product.objects.exists():
                    # store/apps.py se 2 level upar main root folder par jaane ke liye
                    current_dir = os.path.dirname(os.path.abspath(__file__)) # Yeh 'store' folder hai
                    base_dir = os.path.dirname(current_dir) # Yeh main root folder hai jahan manage.py hai
                    json_path = os.path.join(base_dir, 'products.json')
                    
                    if os.path.exists(json_path):
                        call_command('loaddata', json_path)
                        print("Successfully loaded products.json!")
                    else:
                        print(f"products.json not found at: {json_path}")

        except Exception as e:
            print(f"Error during app ready: {e}")
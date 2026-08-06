from django.apps import AppConfig

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signal # Signal file ko load karein

from django.apps import AppConfig

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        try:
            from django.contrib.sites.models import Site
            Site.objects.get_or_create(id=1, defaults={'domain': 'bloomcart-30cs.onrender.com', 'name': 'BloomCart'})
        except Exception:
            pass

from django.apps import AppConfig
import os

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp

            # 1. Ensure Site ID 1 exists
            site, created = Site.objects.get_or_create(
                id=1, 
                defaults={'domain': 'bloomcart-30cs.onrender.com', 'name': 'BloomCart'}
            )
            if not created:
                site.domain = 'bloomcart-30cs.onrender.com'
                site.save()

            # 2. Ensure Google SocialApp exists to prevent DoesNotExist error
            # Yahan hum Render ke environment variables utha rahe hain, agar wahan nahi hain toh default dummy daal rahe hain taaki crash na ho
            client_id = os.getenv('GOOGLE_CLIENT_ID', 'dummy_client_id')
            secret = os.getenv('GOOGLE_SECRET', 'dummy_secret')
            
            app, app_created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': client_id,
                    'secret': secret,
                }
            )
            if not app.sites.filter(id=site.id).exists():
                app.sites.add(site)
                
        except Exception:
            pass

from django.apps import AppConfig
from django.contrib.auth.models import User

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        try:
            # Check karega ki koi superuser pehle se hai ya nahi
            if not User.objects.filter(is_superuser=True).exists():
                # Yahan aap apna manchaha username, email aur password set kar sakte hain
                User.objects.create_superuser('kanishk', 'kanishkmeenakshisharma06@gmail.com', 'kanishk@13')
        except Exception:
            pass
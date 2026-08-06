from django.apps import AppConfig
import os

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # 1. Signals ko load karein
        try:
            import store.signal  # ya 'store.signals' agar file ka naam plural hai
        except ImportError:
            pass

        # 2. Database entries (Site, SocialApp, Superuser)
        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp
            from django.contrib.auth.models import User

            # Site ID 1 ensure karein
            site, created = Site.objects.get_or_create(
                id=1, 
                defaults={'domain': 'bloomcart-30cs.onrender.com', 'name': 'BloomCart'}
            )
            if not created:
                site.domain = 'bloomcart-30cs.onrender.com'
                site.save()

            # Google SocialApp ensure karein (DoesNotExist error fix karne ke liye)
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

            # Superuser ensure karein
            if not User.objects.filter(username='kanishk').exists():
                User.objects.create_superuser('kanishk', 'kanishkmeenakshisharma06@gmail.com', 'kanishk@13')

        except Exception:
            pass
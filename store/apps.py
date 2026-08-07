from django.apps import AppConfig
import os

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Python 3.14 + Django template context fix for Admin panel
        try:
            from django.template.context import Context
            if hasattr(Context, '__copy__'):
                orig_copy = Context.__copy__
                def patched_copy(self):
                    try:
                        return orig_copy(self)
                    except AttributeError:
                        # Fallback copy method for Python 3.14 compatibility
                        dup = self.__class__()
                        dup.dicts = list(self.dicts)
                        return dup
                Context.__copy__ = patched_copy
        except Exception:
            pass

        # Baaki purana code (Signals, Site, SocialApp, Superuser)
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
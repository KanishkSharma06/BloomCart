import os
from celery import Celery

# Yahan 'bloomcart_project.settings' bilkul sahi format mein hona chahiye
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloomcart_project.settings')

app = Celery('bloomcart_project')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
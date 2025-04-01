from __future__ import absolute_import, unicode_literals
from celery import Celery

# Initialize Celery application
app = Celery('hotel_booking')

# Load configuration from Django settings, using the CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
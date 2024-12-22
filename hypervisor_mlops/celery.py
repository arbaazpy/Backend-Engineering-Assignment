from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervisor_mlops.settings')

app = Celery('hypervisor_mlops', broker=settings.CELERY_BROKER_URL)

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

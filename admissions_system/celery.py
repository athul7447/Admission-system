# project_name/celery.py

import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admissions_system.settings')

app = Celery('admissions_system')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from apps
app.autodiscover_tasks()


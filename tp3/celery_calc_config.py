
from celery import Celery

app = Celery('celery_calc', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0', include=['celery_calc'])

# 'redis://analytics.juncotic.com:6379'

# Running the celery worker server
# celery -A celery_calc worker --loglevel=info
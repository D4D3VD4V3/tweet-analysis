web: gunicorn app:app
worker: celery worker -A app.tasks --loglevel=INFO

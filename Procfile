web: gunicorn app:run
worker: celery worker -A app.tasks --loglevel=INFO

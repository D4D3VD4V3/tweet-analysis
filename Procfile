web: gunicorn run:app
worker: celery worker -A app.tasks --loglevel=INFO

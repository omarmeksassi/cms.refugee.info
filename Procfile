web: gunicorn cms_refugeeinfo.wsgi --timeout 120 --log-file -
worker: celery -A cms_refugeeinfo worker --loglevel=info

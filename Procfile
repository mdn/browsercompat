web: newrelic-admin run-program gunicorn wpcsite.wsgi
worker: newrelic-admin run-program celery worker --autoscale=3,1 --app=wpcsite.celery

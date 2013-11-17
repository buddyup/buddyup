web: gunicorn buddyup:app -w 4 -k gevent_wsgi
init: python ./scripts/create-database.py
mockcas: python ./mockcas/mockcas.py

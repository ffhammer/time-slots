flask init-db
exec gunicorn -b 0.0.0.0:5005 src.app:app

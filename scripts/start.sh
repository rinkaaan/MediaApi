#(cd api && flask run --host=0.0.0.0 --port $PORT)
#(cd .. && PYTHONPATH=. python api/app.py)
#(cd .. && export PORT=34201 PYTHONPATH=. && gunicorn -w 1 'api.app:app' -b 0.0.0.0:$PORT)
(export PYTHONPATH=. && gunicorn -w 1 'api.app:app' -b 0.0.0.0:$PORT)


"""Nimbodata gunicorn config."""

bind = ['0.0.0.0:5000']
workers = 5
worker_class = 'gevent'
timeout = 1000000
errorlog = '-'

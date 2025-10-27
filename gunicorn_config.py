# Gunicorn configuration for production deployment
# Usage: gunicorn --config gunicorn_config.py epcdata.wsgi:application

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = 'vanparts-direct'

# Server mechanics
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn/vanparts-direct.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if using Gunicorn for SSL termination)
# For production, recommend using Nginx as reverse proxy instead
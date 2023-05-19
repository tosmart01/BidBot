import os
bind = "0.0.0.0:7777"
workers = os.cpu_count()
backlog = 2048
timeout = 600
debug = False
capture_output = True
max_requests = 50000
max_requests_jitter = 1000
worker_connections = 5000
keepalive = 2

#!/usr/bin/bash


gunicorn -b 0.0.0.0:5000 --worker-class=gevent --worker-connections=1000 --workers=3  app:app -D

echo 'proxy-app running.'

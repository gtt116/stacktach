import eventlet
# NOTE(gtt): Make sure monkey_patch() before import django.*
eventlet.monkey_patch()
from eventlet import wsgi

import yaml
from stacktach import app
from stacktach.worker import manager
from stacktach.common import log

# TODO: First start create database

if __name__ == '__main__':
    log.setup_log()
    deployments = yaml.load(file('etc/deployments.yaml').read())
    manager.start_consume(deployments['deployments'])

    wsgi.server(eventlet.listen(('0.0.0.0', 8000)), app.application)

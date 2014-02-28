import eventlet
# NOTE(gtt): Make sure monkey_patch() before import django.*
eventlet.monkey_patch()
from eventlet import wsgi

import yaml
from stacktach import app
from stacktach.worker import worker

# TODO: First start create database

if __name__ == '__main__':
    deployments = yaml.load(file('etc/deployments.yaml').read())
    for d in deployments['deployments']:
        eventlet.spawn_n(
            worker.run, d
        )

    wsgi.server(eventlet.listen(('0.0.0.0', 8000)), app.application)

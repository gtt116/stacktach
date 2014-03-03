import logging

import kombu
import eventlet

from stacktach import models
from stacktach.worker import worker

LOG = logging.getLogger(__name__)

MANAGER = None


class ConsumerManager(object):
    def __init__(self, deployments):
        assert isinstance(deployments, list)
        self._deployments = deployments
        self._consumers = []

    def start(self):
        """Start each consumer in a greenlet."""
        for deploy in self._deployments:
            eventlet.spawn_n(self._start_consumer, deploy)

    def consumer_status(self):
        """
        Return a map of consumer name and consumer processed message count.
        """
        status = {}

        for consumer in self._consumers:
            status[consumer.name] = consumer.total_processed

        return status

    def _start_consumer(self, deployment_config):
        name = deployment_config['name']
        host = deployment_config.get('rabbit_host', 'localhost')
        port = deployment_config.get('rabbit_port', 5672)
        user_id = deployment_config.get('rabbit_userid', 'guest')
        password = deployment_config.get('rabbit_password', '')
        virtual_host = deployment_config.get('rabbit_virtual_host', '/')
        durable = deployment_config.get('durable_queue', False)

        deployment, new = models.get_or_create_deployment(name)

        LOG.info("Starting worker for '%s'" % name)
        LOG.info("name: %s: host:%s port:%s user_id:%s virtual_host:%s" %
                (name, host, port, user_id, virtual_host))

        params = dict(hostname=host,
                    port=port,
                    virtual_host=virtual_host)

        if user_id:
            params['userid'] = user_id
        if password:
            params['password'] = password

        while True:
            LOG.debug("Processing on '%s'" % name)
            with kombu.connection.BrokerConnection(**params) as conn:
                try:
                    consumer = worker.NovaConsumer(name, conn,
                                                   deployment, durable)
                    self._consumers.append(consumer)
                    consumer.run()
                except Exception as e:
                    LOG.exception("name=%s, exception=%s. Reconnecting in 5s" %
                                    (name, e))
                    eventlet.sleep(5)
            LOG.debug("Completed processing on '%s'" % name)


def start_consume(deployments):
    global MANAGER
    assert MANAGER is None, "start_consume() should only invoke once."
    MANAGER = ConsumerManager(deployments)
    MANAGER.start()


def consumer_status():
    return MANAGER.consumer_status()

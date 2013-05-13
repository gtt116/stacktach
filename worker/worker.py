# Copyright 2012 - Dark Secret Software Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This is the worker you run in your OpenStack environment. You need
# to set TENANT_ID and URL to point to your StackTach web server.

import datetime
import json
import kombu
import kombu.connection
import kombu.entity
from kombu import Consumer
import logging
import time

from pympler.process import ProcessMemoryInfo

from stacktach import models, views


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler('worker.log',
                                           when='h', interval=6, backupCount=4)
LOG.addHandler(handler)


class NovaConsumer():
    def __init__(self, name, connection, deployment, durable):
        self.connection = connection
        self.deployment = deployment
        self.durable = durable
        self.name = name
        self.last_time = None
        self.pmi = None
        self.processed = 0
        self.total_processed = 0
        self.channel = connection.channel()

        self.nova_exchange = kombu.entity.Exchange("nova", type="topic",
                                    exclusive=False, durable=self.durable,
                                    auto_delete=False)

        self.nova_queues = [
            kombu.Queue("stacktash.notifications.info", self.nova_exchange,
                        durable=self.durable, auto_delete=False,
                        exclusive=False, routing_key='notifications.info'),
            kombu.Queue("stacktash.notifications.error", self.nova_exchange,
                        durable=self.durable, auto_delete=False,
                        exclusive=False, routing_key='notifications.error'),
        ]

        self.consumer = Consumer(channel=self.channel,
                            queues=self.nova_queues, callbacks=[self.on_nova])

    def run(self):
        while True:
            self.consumer.consume()
            self.connection.drain_events()
            time.sleep(1)

    def _process(self, body, message):
        routing_key = message.delivery_info['routing_key']
        payload = (routing_key, body)
        # make sure jsonable body.
        json.dumps(payload)

        body = str(message.body)
        args = (routing_key, json.loads(body))
        asJson = json.dumps(args)

        raw = views.process_raw_data(self.deployment, args, asJson)
        if raw:
            self.processed += 1

        self._check_memory()

    def _check_memory(self):
        if not self.pmi:
            self.pmi = ProcessMemoryInfo()
            self.last_vsz = self.pmi.vsz
            self.initial_vsz = self.pmi.vsz

        utc = datetime.datetime.utcnow()
        check = self.last_time is None
        if self.last_time:
            diff = utc - self.last_time
            if diff.seconds > 30:
                check = True
        if check:
            self.last_time = utc
            self.pmi.update()
            diff = (self.pmi.vsz - self.last_vsz) / 1000
            idiff = (self.pmi.vsz - self.initial_vsz) / 1000
            self.total_processed += self.processed
            per_message = 0
            if self.total_processed:
                per_message = idiff / self.total_processed
            LOG.debug("%20s %6dk/%6dk ram, "
                      "%3d/%4d msgs @ %6dk/msg" %
                      (self.name, diff, idiff, self.processed,
                      self.total_processed, per_message))
            self.last_vsz = self.pmi.vsz
            self.processed = 0

    def on_nova(self, body, message):
        try:
            self._process(body, message)
        except Exception, e:
            LOG.exception("Problem %s" % e)
        finally:
            message.ack()


def run(deployment_config):
    name = deployment_config['name']
    host = deployment_config.get('rabbit_host', 'localhost')
    port = deployment_config.get('rabbit_port', 5672)
    user_id = deployment_config.get('rabbit_userid', 'rabbit')
    password = deployment_config.get('rabbit_password', 'rabbit')
    virtual_host = deployment_config.get('rabbit_virtual_host', '/')
    durable = deployment_config.get('durable_queue', True)

    deployment, new = models.get_or_create_deployment(name)

    print "Starting worker for '%s'" % name
    LOG.info("%s: %s %s %s %s" % (name, host, port, user_id, virtual_host))

    params = dict(hostname=host,
                  port=port,
                  virtual_host=virtual_host)

    if user_id:
        params.update('userid', user_id)
    if password:
        params.update('password', password)

    while True:
        LOG.debug("Processing on '%s'" % name)
        with kombu.connection.BrokerConnection(**params) as conn:
            try:
                consumer = NovaConsumer(name, conn, deployment, durable)
                consumer.run()
            except Exception as e:
                LOG.exception("name=%s, exception=%s. Reconnecting in 5s" %
                                (name, e))
                time.sleep(5)
        LOG.debug("Completed processing on '%s'" % name)

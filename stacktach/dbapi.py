import datetime

import yaml
from django import db

from stacktach import models
from stacktach import mailer
from stacktach import datetime_to_decimal as dt


def _extract_states(payload):
    return {
        'state': payload.get('state', ""),
        'old_state': payload.get('old_state', ""),
        'old_task': payload.get('old_task_state', "")
    }


def mail_and_save(routing_key, body):
    obj = _monitor_message(routing_key, body)
    subject = 'Get %(event)s from %(host)s' % obj
    payload = yaml.safe_dump(body)
    mailer.send(subject, payload)
    return obj


def _monitor_message(routing_key, body):
    event = body['event_type']
    publisher = body['publisher_id']
    request_id = body['_context_request_id']
    parts = publisher.split('.')
    service = parts[0]
    if len(parts) > 1:
        host = ".".join(parts[1:])
    else:
        host = None
    payload = body['payload']

    # instance UUID's seem to hide in a lot of odd places.
    instance = payload.get('instance_id', None)
    instance = payload.get('instance_uuid', instance)
    try:
        if not instance:
            instance = payload.get('exception', {}).get('kwargs', {}).get('uuid')
    except AttributeError:
        #FIXME: LOG.warn here
        instance = None
    if not instance:
        instance = payload.get('instance', {}).get('uuid')

    tenant = body.get('_context_project_id', None)
    tenant = payload.get('tenant_id', tenant)

    tenant_name = body.get('_context_project_name', None)
    resp = dict(host=host, instance=instance, publisher=publisher,
                service=service, event=event, tenant=tenant,
                request_id=request_id, tenant_name=tenant_name)
    resp.update(_extract_states(payload))
    return resp


def _compute_update_message(routing_key, body):
    publisher = None
    instance = None
    args = body['args']
    host = args['host']
    request_id = body['_context_request_id']
    service = args['service_name']
    event = body['method']
    tenant = args.get('_context_project_id', None)
    resp = dict(host=host, instance=instance, publisher=publisher,
                service=service, event=event, tenant=tenant,
                request_id=request_id)
    payload = body.get('payload', {})
    resp.update(_extract_states(payload))
    return resp


# routing_key : handler
HANDLERS = {'notifications.info': _monitor_message,
            'notifications.error': mail_and_save,
            '': _compute_update_message}


def start_kpi_tracking(lifecycle, raw):
    """Start the clock for kpi timings when we see an instance.update
    coming in from an api node."""
    if raw.event != "compute.instance.update":
        return

    if "api" not in raw.host:
        return

    tracker = models.RequestTracker(request_id=raw.request_id,
                                    start=raw.when,
                                    lifecycle=lifecycle,
                                    last_timing=None,
                                    duration=str(0.0))
    tracker.save()


def update_kpi(lifecycle, timing, raw):
    """Whenever we get a .end event, use the Timing object to
    compute our current end-to-end duration.

    Note: it may not be completely accurate if the operation is
    still in-process, but we have no way of knowing it's still
    in-process without mapping the original command with the
    expected .end event (that's a whole other thing)

    Until then, we'll take the lazy route and be aware of these
    potential fence-post issues."""
    trackers = models.RequestTracker.objects.\
                                        filter(request_id=raw.request_id)
    if len(trackers) == 0:
        return

    tracker = trackers[0]
    tracker.last_timing = timing
    tracker.duration = timing.end_when - tracker.start
    tracker.save()


def aggregate(raw):
    """Roll up the raw event into a Lifecycle object
    and a bunch of Timing objects.

    We can use this for summarized timing reports.

    Additionally, we can use this processing to give
    us end-to-end user request timings for kpi reports.
    """

    if not raw.instance:
        return

    # While we hope only one lifecycle ever exists it's quite
    # likely we get multiple due to the workers and threads.
    lifecycle = None
    lifecycles = models.Lifecycle.objects.select_related().\
                                    filter(instance=raw.instance)
    if len(lifecycles) > 0:
        lifecycle = lifecycles[0]
    if not lifecycle:
        lifecycle = models.Lifecycle(instance=raw.instance)
    lifecycle.last_raw = raw
    lifecycle.last_state = raw.state
    lifecycle.last_task_state = raw.old_task
    lifecycle.save()

    event = raw.event
    parts = event.split('.')
    step = parts[-1]
    name = '.'.join(parts[:-1])

    if not step in ['start', 'end']:
        # Perhaps it's an operation initiated in the API?
        start_kpi_tracking(lifecycle, raw)
        return

    # We are going to try to track every event pair that comes
    # through, but that's not as easy as it seems since we don't
    # have a unique key for each request (request_id won't work
    # since the call could come multiple times via a retry loop).
    # So, we're just going to look for Timing objects that have
    # start_raw but no end_raw. This could give incorrect data
    # when/if we get two overlapping foo.start calls (which
    # *shouldn't* happen).
    start = step == 'start'
    timing = None
    timings = models.Timing.objects.select_related().\
                                filter(name=name, lifecycle=lifecycle)
    if not start:
        for t in timings:
            try:
                if t.end_raw == None and t.start_raw != None:
                    timing = t
                    break
            except models.RawData.DoesNotExist:
                # Our raw data was removed.
                pass

    if timing is None:
        timing = models.Timing(name=name, lifecycle=lifecycle)

    if start:
        timing.start_raw = raw
        timing.start_when = raw.when

        # Erase all the other fields which may have been set
        # the first time this operation was performed.
        # For example, a resize that was done 3 times:
        # We'll only record the last one, but track that 3 were done.
        timing.end_raw = None
        timing.end_when = None

        timing.diff_when = None
        timing.diff_ms = 0
    else:
        timing.end_raw = raw
        timing.end_when = raw.when

        # We could have missed start so watch out ...
        if timing.start_when:
            timing.diff = timing.end_when - timing.start_when
            # Looks like a valid pair ...
            update_kpi(lifecycle, timing, raw)
    timing.save()


def process_raw_data(deployment, args, json_args):
    """This is called directly by the worker to add the event to the db."""
    db.reset_queries()

    routing_key, body = args
    record = None
    handler = HANDLERS.get(routing_key, None)
    if handler:
        values = handler(routing_key, body)
        if not values:
            return record

        values['deployment'] = deployment
        try:
            when = body['timestamp']
        except KeyError:
            when = body['_context_timestamp']  # Old way of doing it
        try:
            try:
                when = datetime.datetime.strptime(when, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                # Old way of doing it
                when = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception:
            pass
        values['when'] = dt.dt_to_decimal(when)
        values['routing_key'] = routing_key
        values['json'] = json_args
        record = models.RawData(**values)
        record.save()

        aggregate(record)
    return record

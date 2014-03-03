# Copyright 2012 - Dark Secret Software Inc.
# Copyright 2014 - gtt116
import yaml

from django.shortcuts import render_to_response

from stacktach import models
from stacktach import datetime_to_decimal as dt
from stacktach.worker import manager

import datetime
import json


def _post_process_raw_data(rows, highlight=None):
    for row in rows:
        if "error" in row.routing_key:
            row.is_error = True
        if highlight and row.id == int(highlight):
            row.highlight = True
        row.fwhen = dt.dt_from_decimal(row.when)


def _default_context(request, deployment_id=0):
    deployment = None
    if 'deployment' in request.session:
        d = request.session['deployment']
        if d.id == deployment_id:
            deployment = d

    if not deployment and deployment_id:
        try:
            deployment = models.Deployment.objects.get(id=deployment_id)
            request.session['deployment'] = deployment
        except models.Deployment.DoesNotExist:
            pass

    # Get worker status

    context = dict(
        utc=datetime.datetime.utcnow(),
        deployment=deployment,
        deployment_id=deployment_id,
    )

    status = manager.consumer_status()
    if deployment:
        deployment_processed = status.get(deployment.name)
        context['deployment_processed'] = deployment_processed

    return context


def welcome(request):
    deployments = models.Deployment.objects.all().order_by('name')
    context = _default_context(request)
    context['deployments'] = deployments
    return render_to_response('welcome.html', context)


def home(request, deployment_id):
    context = _default_context(request, deployment_id)
    return render_to_response('index.html', context)


def details(request, deployment_id, column, row_id):
    deployment_id = int(deployment_id)
    c = _default_context(request, deployment_id)
    rows = models.RawData.objects.select_related()
    row = models.RawData.objects.get(pk=row_id)
    value = getattr(row, column)
    if deployment_id:
        rows = rows.filter(deployment=deployment_id)
    if column != 'when':
        rows = rows.filter(**{column: value})
    else:
        when = dt.dt_from_decimal(value)
        from_time = when - datetime.timedelta(minutes=1)
        to_time = when + datetime.timedelta(minutes=1)
        from_time_dec = dt.dt_to_decimal(from_time)
        to_time_dec = dt.dt_to_decimal(to_time)
        rows = rows.filter(when__range=(from_time_dec, to_time_dec))

    rows = rows.order_by('-when')[:200]
    _post_process_raw_data(rows, highlight=row_id)
    c['rows'] = rows
    c['allow_expansion'] = True
    c['show_absolute_time'] = True
    return render_to_response('rows.html', c)


def expand(request, deployment_id, row_id):
    c = _default_context(request, deployment_id)
    row = models.RawData.objects.get(pk=row_id)
    payload = json.loads(row.json)
    payload = yaml.safe_dump(payload)
    c["payload"] = payload
    return render_to_response('expand.html', c)


def latest_raw(request, deployment_id):
    """This is the 2sec ticker that updates the Recent Activity box."""
    deployment_id = int(deployment_id)
    c = _default_context(request, deployment_id)
    query = models.RawData.objects.select_related()
    if deployment_id > 0:
        query = query.filter(deployment=deployment_id)
    rows = query.order_by('-when')[:20]
    _post_process_raw_data(rows)
    c['rows'] = rows
    return render_to_response('host_status.html', c)


def search(request, deployment_id):
    c = _default_context(request, deployment_id)
    column = request.POST.get('field', None)
    value = request.POST.get('value', None)
    updates = request.POST.get('updates', 'true')
    count = request.POST.get('count', 20)

    if updates and updates == 'true':
        updates = True
    else:
        updates = False

    rows = None
    if column != None and value != None:
        rows = models.RawData.objects.select_related()

        # Process deployment_id
        if deployment_id:
            rows = rows.filter(deployment=deployment_id)

        rows = rows.filter(**{column: value})

        # Exclude update message?
        if not updates:
            rows = rows.exclude(event='compute.instance.update')

        rows = rows.order_by('-when')

        # Show all?
        if count != 'All':
            rows = rows[:int(count)]

        _post_process_raw_data(rows)
    c['rows'] = rows
    c['allow_expansion'] = True
    c['show_absolute_time'] = True
    return render_to_response('rows.html', c)


def _pretty_times(times):
    for time in times:
        time.fstart_when = dt.dt_from_decimal(time.start_when)
        time.fend_when = dt.dt_from_decimal(time.end_when)
    return times


def lifecycle(request, deployment_id, instance_id):
    c = _default_context(request, deployment_id)
    lifecycle = models.Lifecycle.objects.get(instance=instance_id)
    times = models.Timing.objects.all().\
                    filter(lifecycle=lifecycle)
    c['lifecycle'] = lifecycle
    c['times'] = _pretty_times(times)
    return render_to_response('lifecycle.html', c)

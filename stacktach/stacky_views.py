from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from stacktach import stacky_server


def monkey_patch_stacky(func):
    """
    Origin stacky server return a HttpReponse object. But we need a json
    object. So monkey patch it before process, and then reverting when
    finished.
    """
    def patched_rsp(json):
        header = json.pop(0)
        return {'header': header, 'data': json}

    def inner(*args, **kwargs):
        origin_rsp = stacky_server.rsp
        stacky_server.rsp = patched_rsp
        response = func(*args, **kwargs)
        stacky_server.rsp = origin_rsp
        return response

    return inner


@monkey_patch_stacky
def summary(request, deployment_id):
    resp = stacky_server.do_summary(request)
    resp['url_prefix'] = reverse('timings', args=[deployment_id]) + '?name='
    resp['subtitle'] = 'Summary'
    return render_to_response('stacky.html', resp)


@monkey_patch_stacky
def timings(request, deployment_id):
    resp = stacky_server.do_timings(request)
    resp['url_prefix'] = reverse('timings_uuid', args=[deployment_id]) \
            + '?uuid='
    resp['subtitle'] = 'Events Timings'
    return render_to_response('stacky.html', resp)


@monkey_patch_stacky
def timings_uuid(request, deployment_id):
    resp = stacky_server.do_timings_uuid(request)
    resp['subtitle'] = 'Instance Timings'
    return render_to_response('stacky.html', resp)

from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'stacktach.views.welcome', name='welcome'),

    url(r'stacky/deployments/$', 'stacktach.stacky_server.do_deployments'),
    url(r'stacky/events/$', 'stacktach.stacky_server.do_events'),
    url(r'stacky/hosts/$', 'stacktach.stacky_server.do_hosts'),
    url(r'stacky/uuid/$', 'stacktach.stacky_server.do_uuid'),
    url(r'stacky/timings/$', 'stacktach.stacky_server.do_timings'),
    url(r'stacky/timings/uuid$', 'stacktach.stacky_server.do_timings_uuid'),
    url(r'stacky/summary/$', 'stacktach.stacky_server.do_summary'),
    url(r'stacky/request/$', 'stacktach.stacky_server.do_request'),
    url(r'stacky/show/(?P<event_id>\d+)/$',
        'stacktach.stacky_server.do_show'),
    url(r'stacky/watch/(?P<deployment_id>\d+)/$',
        'stacktach.stacky_server.do_watch'),
    url(r'stacky/kpi/$', 'stacktach.stacky_server.do_kpi'),
    url(r'stacky/kpi/(?P<tenant_id>\d+)/$', 'stacktach.stacky_server.do_kpi'),

    url(r'^(?P<deployment_id>\d+)/$', 'stacktach.views.home', name='home'),
    url(r'^(?P<deployment_id>\d+)/details/(?P<column>\w+)/(?P<row_id>\d+)/$',
        'stacktach.views.details', name='details'),
    url(r'^(?P<deployment_id>\d+)/search/$',
        'stacktach.views.search', name='search'),
    url(r'^(?P<deployment_id>\d+)/expand/(?P<row_id>\d+)/$',
        'stacktach.views.expand', name='expand'),
    url(r'^(?P<deployment_id>\d+)/lifecycle/(?P<instance_id>.+)/$',
        'stacktach.views.lifecycle', name='lifecycle'),
    url(r'^(?P<deployment_id>\d+)/latest_raw/$',
        'stacktach.views.latest_raw', name='latest_raw'),
)

urlpatterns += patterns(
    'stacktach.stacky_views',
    url(r'^(?P<deployment_id>\d+)/summary/$', 'summary', name='summary'),
    url(r'^(?P<deployment_id>\d+)/timings/$', 'timings', name='timings'),
    url(r'^(?P<deployment_id>\d+)/timings/uuid$', 'timings_uuid',
        name='timings_uuid'),
)

urlpatterns += staticfiles_urlpatterns()

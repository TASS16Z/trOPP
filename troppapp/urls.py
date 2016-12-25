# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns
from troppapp.views import OPPListView, OPPDetailView, PersonListView, PersonDetailView

urlpatterns = patterns(
    'troppapp.views',
    # Index view
    url(r'^$', 'index'),
    url(r'^OPP/$', OPPListView.as_view(), name='opp-list'),
    url(r'^OPP/(?P<pk>[\d]+)/$', OPPDetailView.as_view(), name='opp-detail'),
    url(r'^persons/$', PersonListView.as_view(), name='person-list'),
    url(r'^persons/(?P<pk>[\d]+)/$',
        PersonDetailView.as_view(),
        name='person-detail'),
)

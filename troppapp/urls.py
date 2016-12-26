# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns
from troppapp.views import (
    OPPListView,
    OPPDetailView,
    PersonListView,
    PersonDetailView,
    opp_by_city,
    opp_by_legal_form,
    opp_by_board_members,
    opp_by_area,
    details
)

urlpatterns = patterns(
    'troppapp.views',
    # Index view
    url(r'^$', 'index'),
    url(r'^OPP/$', OPPListView.as_view(), name='opp-list'),
    url(r'^api/opp_by_city', opp_by_city, name='opp_by_city'),
    url(r'^api/opp_by_legal_form', opp_by_legal_form, name='opp_by_legal_form'),
    url(r'^api/opp_by_board_members', opp_by_board_members, name='opp_by_board_members'),
    url(r'^api/opp_by_area', opp_by_area, name='opp_by_area'),
    url(r'^api/details', details, name='details'),
    url(r'^OPP/(?P<pk>[\d]+)/$', OPPDetailView.as_view(), name='opp-detail'),
    url(r'^persons/$', PersonListView.as_view(), name='person-list'),
    url(r'^persons/(?P<pk>[\d]+)/$',
        PersonDetailView.as_view(),
        name='person-detail'),
)

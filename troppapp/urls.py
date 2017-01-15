from django.conf.urls import url, patterns
from troppapp.views import *
urlpatterns = patterns(
    'troppapp.views',
    # Index view
    url(r'^$', 'index'),
    url(r'^OPP/$', OPPListView.as_view(), name='opp-list'),
    url(r'^api/node_click', node_click, name='node_click'),
    url(r'^api/voivodeships', voivodeships, name='voivodeships'),
    url(r'^api/legal_forms', legal_forms, name='legal_forms'),
    url(r'^api/areas', areas, name='areas'),
    url(r'^api/details', details, name='details'),
    url(r'^OPP/(?P<pk>[\d]+)/$', OPPDetailView.as_view(), name='opp-detail'),
)

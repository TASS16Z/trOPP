import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from troppapp.models import OPP, Person, City, LegalForm, PublicBenefitArea
from trOPP import db

class OPPDetailView(DetailView):
    model = OPP

class OPPListView(ListView):
    model = OPP

class PersonDetailView(DetailView):
    model = Person

class PersonListView(ListView):
    model = Person

def index(request):
    return render(request, 'index.html')

def _get_graph(class_node, class_edge, connection):
    nodes = []
    links = []
    for node in class_node.objects.all():
        nodes.append(node.get_json())
    for edge in class_edge.objects.all():
        nodes.append(edge.get_json())
        for node in getattr(edge, connection):
            links.append({ 'source' : node.handle_id,
                           'target' : edge.handle_id })
    response_data = {}
    response_data['nodes'] = nodes
    response_data['links'] = links
    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def opp_by_city(request):
    return _get_graph(OPP, City, "opps")

def opp_by_legal_form(request):
    return _get_graph(OPP, LegalForm, "opps")

def opp_by_board_members(request):
    return _get_graph(OPP, Person, "opps")

def opp_by_area(request):
    return _get_graph(OPP, PublicBenefitArea, "opps")

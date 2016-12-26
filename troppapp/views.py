import json
from itertools import combinations
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

def _get_graph(class_node, class_edge, connection, isDirect):
    nodes = []
    links = []
    for node in class_node.objects.all():
        nodes.append(node.get_json())

    for edge in class_edge.objects.all():
        if isDirect == 'true':
            temp = []
            for node in getattr(edge, connection):
                temp.append(node.handle_id)
            links.extend([ { 'source' : i, 'target' : j }
                         for i, j in combinations(temp, 2) ])
        else:
            nodes.append(edge.get_json())
            for node in getattr(edge, connection):
                links.append({ 'source' : node.handle_id,
                               'target' : edge.handle_id })

    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")


def opp_by_city(request):
    return _get_graph(OPP, City, "opps", request.GET['isDirect'])

def opp_by_legal_form(request):
    return _get_graph(OPP, LegalForm, "opps", request.GET['isDirect'])

def opp_by_board_members(request):
    return _get_graph(OPP, Person, "opps", request.GET['isDirect'])

def opp_by_area(request):
    return _get_graph(OPP, PublicBenefitArea, "opps", request.GET['isDirect'])

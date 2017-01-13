from neo4j import contextmanager
from django.conf import settings
import json
from itertools import combinations
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from troppapp.models import OPP, Person, City, LegalForm, PublicBenefitArea
from trOPP import db

manager = contextmanager.Neo4jDBConnectionManager(
    settings.NEO4J_RESOURCE_URI,
    settings.NEO4J_USERNAME,
    settings.NEO4J_PASSWORD)


class OPPDetailView(DetailView):
    model = OPP

class OPPListView(ListView):
    model = OPP
    paginate_by = 20

class PersonDetailView(DetailView):
    model = Person

class PersonListView(ListView):
    model = Person
    paginate_by = 20

def index(request):
    return render(request, 'index.html')

def _get_graph(class_from, class_to, connection, isDirect):
    nodes = []
    links = []
    query = """
        MATCH (n:%s)-[r:%s]->(w:%s) RETURN n.handle_id, w.handle_id
        """ % (class_from.__name__, connection, class_to.__name__) 
    with manager.read as reader:
         links_list = reader.execute(query).fetchall()
         
    nodes_set = set(val for l in links_list for val in l)
    nodes_dict = {d:i for i, d in enumerate(nodes_set) }
    
    for key in nodes_dict.keys():
        nodes.append({ 'name': key })
    
    for link in links_list:
        links.append({ 'source' : nodes_dict[link[0]],
                       'target' : nodes_dict[link[1]] })
    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")

def opp_by_city(request):
    return _get_graph(OPP, City, "REGISTERED_IN", request.GET['isDirect'])

def opp_by_legal_form(request):
    return _get_graph(OPP, LegalForm, "OPERATES_AS", request.GET['isDirect'])

def opp_by_board_members(request):
    return _get_graph(Person, OPP, "MANAGES", request.GET['isDirect'])

def opp_by_area(request):
    return _get_graph(OPP, PublicBenefitArea, "CATEGORY", request.GET['isDirect'])

def _get_class_details(classname, handle_id):
    for c in models.get_models():
        if c.__name__ == classname:
            return c.objects.get(handle_id=handle_id).get_json()
    return ""

def details(request):
    return HttpResponse(json.dumps(_get_class_details(request.GET['class'], request.GET['handle_id'])), content_type="application/json")

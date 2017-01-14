from neo4j import contextmanager
from django.conf import settings
import json
from itertools import combinations
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from troppapp.models import * 
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

def _get_nodes(class_name):
    nodes = []
    links = []
    query = """
        MATCH (n:%s) RETURN n.handle_id
        """ % class_name.__name__ 
    with manager.read as reader:
         nodes_set = reader.execute(query).fetchall()
    for key in nodes_set:
        nodes.append(class_name.objects.get(handle_id=key[0]).get_json())
    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")
        
def _get_children(classname, node_handle):
    nodes = []
    links = []
    for c in models.get_models():
        if c.__name__ == classname:
            caller_class = c
            caller_obj = c.objects.get(handle_id=node_handle)
            break
    # get all siblings
    if caller_class in [Voivodeship, LegalForm, PublicBenefitArea, TerritorialReach]:
        query = """
            MATCH (n:%s) RETURN n.handle_id
            """ % c.__name__ 
        with manager.read as reader:
            nodes_set = reader.execute(query).fetchall()
        for key in nodes_set:
            nodes.append(caller_class.objects.get(handle_id=key[0]).get_json())

    # get siblings with the same parent, connect parent
    else:
        query = """
            MATCH (c1 {handle_id:{handle_id}})-[]->(parent)
            OPTIONAL MATCH (c2)-[]->(parent) WHERE c1 <> c2
            RETURN c1.handle_id, c2.handle_id, labels(parent)[0], parent.handle_id
            """ 
        with manager.read as reader:
            nodes_set = reader.execute(query, handle_id = node_handle).fetchall()
        # append parent node
        for c in models.get_models():
            if c.__name__ == nodes_set[0][2]:
                nodes.append(c.objects.get(handle_id=nodes_set[0][3]).get_json())
        # append caller node
        nodes.append(caller_class.objects.get(handle_id=node_handle).get_json())
        links.append({ "source" : nodes_set[0][3], "target" : node_handle })

        for key in nodes_set:
            if key[1] is not None:
                nodes.append(caller_class.objects.get(handle_id=key[1]).get_json())
                links.append({ "source" : nodes_set[0][3],
                           "target" : key[1] })

    # get children
    query = """
        MATCH (n)-[]->(w {handle_id: {handle_id}})
        RETURN labels(n)[0], n.handle_id
        """ 
    with manager.read as reader:
        links_list = reader.execute(query, handle_id = node_handle).fetchall()

    # children with links
    for link in links_list:
        for c in models.get_models():
            if c.__name__ == link[0]:
                nodes.append(c.objects.get(handle_id=link[1]).get_json())
                links.append({ "source" : node_handle,
                               "target" : link[1] })
    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")

def node_click(request):
    return _get_children(request.GET['class'], request.GET['handle_id'])

def voivodeships(request):
    return _get_nodes(Voivodeship)

def legal_forms(request):
    return _get_nodes(LegalForm)

def areas(request):
    return _get_nodes(Areas)

def _get_class_details(classname, handle_id):
    for c in models.get_models():
        if c.__name__ == classname:
            return c.objects.get(handle_id=handle_id).get_json()
    return ""

def details(request):
    return HttpResponse(json.dumps(_get_class_details(request.GET['class'], request.GET['handle_id'])), content_type="application/json")

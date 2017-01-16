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

def _get_opp_graph(node_handle, rel_type):
    nodes = []
    links = []
    nodes.append(OPP.objects.get(handle_id=node_handle).get_json())
    if rel_type == "people":
        query = """
            MATCH (n:OPP {handle_id:{handle_id}})-[]-(p:Person)
            OPTIONAL MATCH (p)-[]-(q:OPP)
            RETURN p.handle_id, q.handle_id
            """ 
        with manager.read as reader:
            query_result = reader.execute(query, handle_id = node_handle).fetchall()
        people_dict = dict()
        opp_dict = dict()
        for key in query_result:
            people_dict[key[0]] = Person
            opp_dict[key[1]] = OPP
            links.append({ "source" : key[0], "target" : key[1] })
        for key in people_dict:
            nodes.append(Person.objects.get(handle_id=key).get_json())
            links.append({ "source" : node_handle, "target" : key })
        for key in opp_dict:
            nodes.append(OPP.objects.get(handle_id=key).get_json())

    else:
        query = """
            MATCH path=(n:OPP {handle_id:{handle_id}})-[*1..3]-(q:OPP)
            WITH n, q, COUNT(*) as cnt
            WHERE cnt > 1
            RETURN q.handle_id, cnt 
            ORDER BY cnt desc LIMIT 50
            """ 
        with manager.read as reader:
            query_result = reader.execute(query, handle_id = node_handle).fetchall()
        for key in query_result:
            nodes.append(OPP.objects.get(handle_id=key[0]).get_json())
            links.append({ "source" : node_handle, "target" : key[0],
                            "weight": key[1] })
        query = """
            MATCH (n:OPP {handle_id:{handle_id}})-[]->(r)
            OPTIONAL MATCH (r)-[]->(w)
            OPTIONAL MATCH (w)-[]->(z)
            RETURN labels(r)[0], r.handle_id, labels(w)[0], w.handle_id, labels(z)[0], z.handle_id
            """ 
        with manager.read as reader:
            query_result = reader.execute(query, handle_id = node_handle).fetchall()
        nodes_dict = dict()
        for result in query_result:
            for i in range(0,6,2):
                if result[i] is not None:
                    nodes_dict[result[i+1]] = result[i]
                    if i == 0:
                        links.append({ "source" : node_handle, "target" : result[i+1] })
                    else:
                        links.append({ "source" : result[i-1], "target" : result[i+1] })
        for key in nodes_dict:
            for c in models.get_models():
                if c.__name__ == nodes_dict[key]:
                    nodes.append(c.objects.get(handle_id=key).get_json())
    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")
        
def _get_children(classname, node_handle, rel_type):
    nodes = []
    links = []
    for c in models.get_models():
        if c.__name__ == classname:
            caller_class = c
            caller_obj = c.objects.get(handle_id=node_handle)
            break
    if caller_class == OPP:
        return _get_opp_graph(node_handle, rel_type)
    if caller_class in [Voivodeship, LegalForm, 
                                PublicBenefitArea, TerritorialReach]:
        # get all siblings
        query = """
            MATCH (n:%s) RETURN n.handle_id
            """ % c.__name__ 
        with manager.read as reader:
            nodes_set = reader.execute(query).fetchall()
        for key in nodes_set:
            nodes.append(caller_class.objects.get(handle_id=key[0]).get_json())

    else:
        # get siblings with the same parent, connect parent
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

    if caller_class == District: 
        # get children and children of children
        query = """
            MATCH (n)-[]->(w {handle_id: {handle_id}})
            OPTIONAL MATCH (q)-[]->(n)
            RETURN labels(n)[0], n.handle_id, labels(q)[0], q.handle_id
            """ 
        with manager.read as reader:
            query_result = reader.execute(query, handle_id = node_handle).fetchall()
        nodes_dict = dict()
        for x in query_result:
            nodes_dict[x[1]] = (x[0], 1)
            if x[3] is not None: 
                nodes_dict[x[3]] = (x[2], 2)
        for key in nodes_dict:
            for c in models.get_models():
                if c.__name__ == nodes_dict[key][0]:
                    nodes.append(c.objects.get(handle_id=key).get_json())
                    if nodes_dict[key][1] == 1:
                        links.append({ "source" : node_handle,
                                   "target" : key })
                    break
        # link children
        for link in query_result:
            links.append({ "source" : link[1], "target" : link[3] })
    else:
        # get children
        query = """
            MATCH (n)-[]->(w {handle_id: {handle_id}})
            RETURN labels(n)[0], n.handle_id
            LIMIT 50
            """ 
        with manager.read as reader:
            links_list = reader.execute(query, handle_id = node_handle).fetchall()

        # link children
        for link in links_list:
            for c in models.get_models():
                if c.__name__ == link[0]:
                    nodes.append(c.objects.get(handle_id=link[1]).get_json())
                    links.append({ "source" : node_handle,
                                   "target" : link[1] })
    return HttpResponse(json.dumps({'nodes' : nodes, 'links' : links }),
                        content_type="application/json")

def node_click(request):
    return _get_children(request.GET['class'], request.GET['handle_id'], request.GET.get('rel_type', 'similar'))

def voivodeships(request):
    return _get_nodes(Voivodeship)

def legal_forms(request):
    return _get_nodes(LegalForm)

def areas(request):
    return _get_nodes(PublicBenefitArea)

def _get_class_details(classname, handle_id):
    for c in models.get_models():
        if c.__name__ == classname:
            return c.objects.get(handle_id=handle_id).get_json()
    return ""

def details(request):
    return HttpResponse(json.dumps(_get_class_details(request.GET['class'], request.GET['handle_id'])), content_type="application/json")

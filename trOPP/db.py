from neo4j import contextmanager
from django.conf import settings

manager = contextmanager.Neo4jDBConnectionManager(
    settings.NEO4J_RESOURCE_URI,
    settings.NEO4J_USERNAME,
    settings.NEO4J_PASSWORD)


def get_node(handle_id, class_var):
    query = """
        MATCH (n:%s {handle_id:{handle_id}})
        RETURN n
        """ % class_var.__name__ 
    try:
        with manager.read as reader:
            for item in reader.execute(query, handle_id = handle_id).fetchone():
                return item
    except IndexError:
        return {}


def delete_node(handle_id, class_var):
    query = """
        MATCH (n:%s {handle_id:{handle_id}}) OPTIONAL MATCH (n)-[r]-()
        DELETE n, r
        """ % (class_var.__name__,handle_id)
    with manager.transaction as writer:
        writer.execute(query, handle_id = handle_id)


def get_unique_node(class_var, key, value):
    query = """
        MATCH (n:%s {%s:{value}})
        RETURN n LIMIT 1
        """ % (class_var.__name__, key) 
    with manager.read as reader:
        return reader.execute(query, value = value).fetchone()

def get_all(class_from, class_to, relationship, handle_id, directed_in = False):
    arrow_in = ""
    arrow_out = ""
    if directed_in:
        arrow_in = "<"
    else:
        arrow_out = ">"
    query = """
        MATCH (n:%s {handle_id:{handle_id}})%s-[r: %s]-%s(v:%s)
        RETURN v.handle_id
        """  % (class_from.__name__, arrow_in, relationship, arrow_out, class_to.__name__)
    try:
        with manager.read as reader:
            return reader.execute(query, handle_id = handle_id).fetchall()
    except IndexError:
        return {}

def get_one(class_from, class_to, relationship, handle_id, directed_in = False):
    arrow_in = ""
    arrow_out = ""
    if directed_in:
        arrow_in = "<"
    else:
        arrow_out = ">"
    query = """
        MATCH (n:%s {handle_id:{handle_id}})%s-[r: %s]-%s(v:%s)
        RETURN v.handle_id
        """  % (class_from.__name__, arrow_in, relationship, arrow_out, class_to.__name__)
    try:
        with manager.read as reader:
            return reader.execute(query, handle_id = handle_id).fetchone()[0]
    except IndexError:
        return {}

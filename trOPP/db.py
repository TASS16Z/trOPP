from neo4j import contextmanager
from django.conf import settings

manager = contextmanager.Neo4jDBConnectionManager(
    settings.NEO4J_RESOURCE_URI,
    settings.NEO4J_USERNAME,
    settings.NEO4J_PASSWORD)


def get_node(handle_id, class_var):
    query = """
        MATCH (n:%s { handle_id: {handle_id} })
        RETURN n
        """ % class_var.__name__ 
    try:
        with manager.read as reader:
            for item in reader.execute(query, handle_id=handle_id).fetchone():
                return item
    except IndexError:
        return {}


def delete_node(handle_id, class_var):
    query = """
        MATCH (n:%s { handle_id: {handle_id} }) OPTIONAL MATCH (n)-[r]-()
        DELETE n, r
        """ % class_var.__name__ 
    with manager.transaction as writer:
        writer.execute(query, handle_id=handle_id)


def get_unique_node(class_var, key, value):
    query = """
        MATCH (n:%s {%s: {value}})
        RETURN n LIMIT 1
        """ % (class_var.__name__, key) 
    with manager.read as reader:
        return reader.execute(query, value=value).fetchone()


def get_voivodeship(handle_id):
    query = """
        MATCH (n:County {handle_id: {handle_id}})-[r:LIES_IN]->(voivodeship)
        RETURN voivodeship.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchone()


def get_county(handle_id):
    query = """
        MATCH (n:City {handle_id: {handle_id}})-[r:LIES_IN]->(county)
        RETURN county.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchone()

def get_city_opps(handle_id):
    query = """
        MATCH (n:City {handle_id: {handle_id}})<-[r:REGISTERED_IN]-(opp)
        RETURN opp.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()

def get_pba_opps(handle_id):
    query = """
        MATCH (n:PublicBenefitArea {handle_id: {handle_id}})<-[r:CATEGORY]-(opp)
        RETURN opp.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()

def get_tr_opps(handle_id):
    query = """
        MATCH (n:TerritorialReach {handle_id: {handle_id}})<-[r:OPERATES_IN]-(opp)
        RETURN opp.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()

def get_lf_opps(handle_id):
    query = """
        MATCH (n:LegalForm {handle_id: {handle_id}})<-[r:OPERATES_AS]-(opp)
        RETURN opp.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()

def get_person_opps(handle_id):
    query = """
        MATCH (n:Person {handle_id: {handle_id}})-[r:MANAGES]->(opp)
        RETURN opp.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()

def get_board_members(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})<-[r:MANAGES]-(person)
        RETURN person.handle_id, r.role
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()


def get_city(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})-[r:REGISTERED_IN]->(city)
        RETURN city.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchone()


def get_aims(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})-[r:DOES]-(aim)
        RETURN aim.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()


def get_public_benefit_areas(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})-[r:CATEGORY]->
        (public_benefit_area)
        RETURN public_benefit_area.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()


def get_territorial_reach(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})-[r:OPERATES_IN]->
        (territorial_reach)
        RETURN territorial_reach.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchall()


def get_legal_form(handle_id):
    query = """
        MATCH (n:OPP {handle_id: {handle_id}})-[r:OPERATES_AS]->(legal_form)
        RETURN legal_form.handle_id
        """
    with manager.read as reader:
        return reader.execute(query, handle_id=handle_id).fetchone()

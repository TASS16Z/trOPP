import uuid
from django.core.management.base import BaseCommand
from django.db import DatabaseError
from trOPP import db
from troppapp.models import (
    OPP,
    Person,
    Voivodeship,
    District,
    City,
    PublicBenefitArea,
    TerritorialReach,
    LegalForm,
)

class Command(BaseCommand):
    help = """
           Create a NodeHandle and set handle_id for nodes
           missing handle_id property
           """

    def handle(self, *args, **options):
        self._add_objects(OPP)
        self._add_objects(Person)
        self._add_objects(Voivodeship)
        self._add_objects(District)
        self._add_objects(City)
        self._add_objects(PublicBenefitArea)
        self._add_objects(TerritorialReach)
        self._add_objects(LegalForm)

    def _add_objects(self, class_var):
        with db.manager.transaction as writer:
            writer.execute('CREATE INDEX ON : %s(handle_id)'
                           % class_var.__name__)
        query = """
                MATCH (m:%s) WHERE m.handle_id IS NULL
                WITH collect(id(m)) as objs
                RETURN objs
                """ % class_var.__name__ 
        try:
            with db.manager.read as reader:
                collection = reader.execute(query).fetchone()[0]
        except IndexError:
            collection = []
        objs = []
        count = 0
        query2 = 'START n = node({node_id}) SET n.handle_id = {handle_id}'
        with db.manager.transaction as writer:
            try:
                for node_id in collection:
                    obj = class_var(handle_id=str(uuid.uuid4()))
                    objs.append(obj)
                    writer.execute(query2,
                                   node_id=node_id,
                                   handle_id=obj.handle_id)
                    count += 1
            except Exception as exception:
                raise exception
            else:
                try:
                    class_var.objects.bulk_create(objs)
                except DatabaseError as exception:
                    writer.connection.rollback()
                    raise exception
            self.stdout.write('Successfully added %d objects of class %s.'
                              % (count, class_var.__name__))

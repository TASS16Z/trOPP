from django.db import models
from django.core.urlresolvers import reverse
from trOPP import db

class NodeHandle(models.Model):
    handle_id = models.CharField(max_length=64, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.name
    def node(self):
        return db.get_node(self.handle_id, self.__class__)
    def delete(self, **kwargs):
        db.delete_node(self.handle_id, self.__class__)
        super(NodeHandle, self).delete()
        return True
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)

class Voivodeship(NodeHandle):
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }

class District(NodeHandle):
    def _voivodeship(self):
        obj_handle = db.get_one(District, Voivodeship, "LIES_IN", self.handle_id)
        return Voivodeship.objects.get(handle_id=obj_handle)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    voivodeship = property(_voivodeship)

class City(NodeHandle):
    def _district(self):
        obj_handle = db.get_one(City, District, "LIES_IN", self.handle_id)
        return District.objects.get(handle_id=obj_handle)
    def _opps(self):
        opps = []
        for obj_handle in db.get_all(City, OPP, "REGISTERED_IN", self.handle_id, directed_in = True):
            opps.append(OPP.objects.get(handle_id=obj_handle))
        return opps
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    district = property(_district)
    opps = property(_opps)

class Aim(NodeHandle):
    pass

class PublicBenefitArea(NodeHandle):
    def _opps(self):
        opps = []
        for obj_handle in db.get_all(PublicBenefitArea, OPP, "CATEGORY", self.handle_id, directed_in = True):
            opps.append(OPP.objects.get(handle_id=obj_handle))
        return opps
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    opps = property(_opps)

class TerritorialReach(NodeHandle):
    def _opps(self):
        opps = []
        for obj_handle in db.get_all(TerritorialReach, OPP, "OPERATES_IN", self.handle_id, directed_in = True):
            opps.append(OPP.objects.get(handle_id=obj_handle))
        return opps
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    opps = property(_opps)

class LegalForm(NodeHandle):
    def _opps(self):
        opps = []
        for obj_handle in db.get_all(LegalForm, OPP, "OPERATES_AS", self.handle_id, directed_in = True):
            opps.append(OPP.objects.get(handle_id=obj_handle))
        return opps
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    opps = property(_opps)

class Person(NodeHandle):
    def get_absolute_url(self):
        return reverse('person-detail', args=[str(self.id)])
    def _opps(self):
        opps = []
        for obj_handle in db.get_all(Person, OPP, "MANAGES", self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle))
        return opps
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }
    opps = property(_opps)

class OPP(NodeHandle):
    def get_absolute_url(self):
        return reverse('opp-detail', args=[str(self.id)])
    def _board_members(self):
        board_members = []
        for obj_handle in db.get_all(OPP, Person, "MANAGES", self.handle_id, directed_in = True):
            board_members.append(Person.objects.get(handle_id=obj_handle))
        return board_members
    def _city(self):
        obj_handle = db.get_one(OPP, City, "REGISTERED_IN", self.handle_id)
        return City.objects.get(handle_id=obj_handle)
    def _aims(self):
        aims = []
        for obj_handle in db.get_all(OPP, Aim, "DOES", self.handle_id):
            aims.append(Aim.objects.get(handle_id=obj_handle))
        return aims
    def _public_benefit_areas(self):
        public_benefit_areas = []
        for obj_handle in db.get_all(OPP, PublicBenefitArea, "CATEGORY", self.handle_id):
            public_benefit_areas.append(
                PublicBenefitArea.objects.get(handle_id=obj_handle))
        return public_benefit_areas
    def _territorial_reach(self):
        territorial_reach = []
        for terr_id in db.get_all(OPP, TerritorialReach, "OPERATES_IN", self.handle_id):
            territorial_reach.append(
                TerritorialReach.objects.get(handle_id=terr_id))
        return territorial_reach
    def _legal_form(self):
        obj_handle = db.get_one(OPP, LegalForm, "OPERATES_AS", self.handle_id)
        return LegalForm.objects.get(handle_id=obj_handle)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'average_salary' : self.node().get('average_salary', 'No salary data'),
                 'class-name' : self.__class__.__name__ }
    def get_fields_and_properties(self):
        field_names = [f.name for f in OPP._meta.fields]
        property_names = [name for name in dir(OPP) if isinstance(getattr(OPP, name), property)]
        return dict((name, getattr(self, name)) for name in field_names + property_names)
    city = property(_city)
    aims = property(_aims)
    public_benefit_areas = property(_public_benefit_areas)
    territorial_reach = property(_territorial_reach)
    legal_form = property(_legal_form)
    board_members = property(_board_members)

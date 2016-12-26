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
        return 'NodeHandle for node %d' % self.node()['handle_id']
    def node(self):
        return db.get_node(self.handle_id, self.__class__)
    def delete(self, **kwargs):
        db.delete_node(self.handle_id, self.__class__)
        super(NodeHandle, self).delete()
        return True

class Voivodeship(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('voivodeship-detail', args=[str(self.id)])
    
class County(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('county-detail', args=[str(self.id)])
    def _voivodeship(self):
        obj_handle = db.get_voivodeship(self.handle_id)[0]
        return Voivodeship.objects.get(handle_id=obj_handle)
    voivodeship = property(_voivodeship)

class City(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('city-detail', args=[str(self.id)])
    def _county(self):
        obj_handle = db.get_county(self.handle_id)[0]
        return County.objects.get(handle_id=obj_handle)
    county = property(_county)
    def _opps(self):
        opps = []
        for obj_handle in db.get_city_opps(self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle[0]))
        return opps
    opps = property(_opps)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }

class Aim(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('aim-detail', args=[str(self.id)])

class PublicBenefitArea(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('public_benefit_area-detail', args=[str(self.id)])
    def _opps(self):
        opps = []
        for obj_handle in db.get_pba_opps(self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle[0]))
        return opps
    opps = property(_opps)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }


class TerritorialReach(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('territorial_reach-detail', args=[str(self.id)])
    def _opps(self):
        opps = []
        for obj_handle in db.get_tr_opps(self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle[0]))
        return opps
    opps = property(_opps)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }


class LegalForm(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return ''#reverse('legal_form-detail', args=[str(self.id)])
    def _opps(self):
        opps = []
        for obj_handle in db.get_lf_opps(self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle[0]))
        return opps
    opps = property(_opps)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }


class Person(NodeHandle):
    def __unicode__(self):
        return self.name
    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)
    def get_absolute_url(self):
        return reverse('person-detail', args=[str(self.id)])
    def _opps(self):
        opps = []
        for obj_handle in db.get_person_opps(self.handle_id):
            opps.append(OPP.objects.get(handle_id=obj_handle[0]))
        return opps
    opps = property(_opps)
    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'class-name' : self.__class__.__name__ }


class OPP(NodeHandle):
    def __unicode__(self):
        return self.name

    def _name(self):
        return self.node().get('name', 'Missing name')
    name = property(_name)

    def get_absolute_url(self):
        return reverse('opp-detail', args=[str(self.id)])
    
    def _board_members(self):
        board_members = []
        for obj_handle, role in db.get_board_members(self.handle_id):
            board_members.append(
                {'person': Person.objects.get(handle_id=obj_handle),
                 'role': role})
        return board_members
    board_members = property(_board_members)

    def _city(self):
        obj_handle = db.get_city(self.handle_id)[0]
        return City.objects.get(handle_id=obj_handle)
    city = property(_city)

    def _aims(self):
        aims = []
        for obj_handle in db.get_aims(self.handle_id):
            aims.append(Aim.objects.get(handle_id=obj_handle))
        return aims
    aims = property(_aims)

    def _public_benefit_areas(self):
        public_benefit_areas = []
        for obj_handle in db.get_public_benefit_areas(self.handle_id)[0]:
            public_benefit_areas.append(
                PublicBenefitArea.objects.get(handle_id=obj_handle))
        return public_benefit_areas
    public_benefit_areas = property(_public_benefit_areas)

    def _territorial_reach(self):
        territorial_reach = []
        for terr_id in db.get_territorial_reach(self.handle_id):
            territorial_reach.append(
                TerritorialReach.objects.get(handle_id=terr_id))
        return territorial_reach
    territorial_reach = property(_territorial_reach)

    def _legal_form(self):
        obj_handle = db.get_legal_form(self.handle_id)[0]
        return LegalForm.objects.get(handle_id=obj_handle)
    legal_form = property(_legal_form)

    def get_json(self):
        return { 'name' : self.name,
                 'id' : self.handle_id,
                 'average_salary' : self.node()['average_salary'],
                 'class-name' : self.__class__.__name__ }

from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from troppapp.models import OPP, Person
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

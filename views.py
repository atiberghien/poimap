from django.views.generic import  CreateView, ListView, DetailView
from models import Hostings
from .forms import HostingsForm

class HostingCreateView(CreateView):
    model = Hostings
    form_class = HostingsForm
    template_name = 'hostings_create.html'

class HostingListView(ListView):
    model = Hostings
    template_name = "hosting_list.html"

class HostingDetailView(DetailView):
    model = Hostings
    template_name = "hosting_detail.html"

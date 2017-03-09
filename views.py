from django.views.generic.edit import CreateView
from models import Hostings

class HostingsCreateView(CreateView):
    model = Hostings
    fields = '__all__'
    template_name = 'hostings_create.html'

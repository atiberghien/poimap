from poimap.models import Area
from .models import Line
from .forms import SearchServiceForm

def transportation(request):
    return {
        "area" : Area.objects.first(),
        "lines" : Line.objects.all(),
        "search_form" : SearchServiceForm()
    }

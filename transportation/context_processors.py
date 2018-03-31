from poimap.models import Area
from .models import Line
from .forms import SearchServiceForm1

def transportation(request):
    return {
        "area" : Area.objects.first(),
        "lines" : Line.objects.all(),
        "form1" : SearchServiceForm1()
    }

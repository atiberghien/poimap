from poimap.models import Area
from .models import Line
from .forms import SearchServiceForm

def transportation(request):
    context = {
        "area" : Area.objects.first(),
        "lines" : Line.objects.all(),
        "search_form" : SearchServiceForm()
    }
    if "travels" in request.session:
        context["cart_size"] = len(request.session["travels"])
    else:
        context["cart_size"] = 0
    return context

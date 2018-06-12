from poimap.models import Area
from .models import Line
from .forms import SearchServiceForm

def transportation(request):
    context = {}
    if "travels" in request.session:
        context["cart_size"] = len(request.session["travels"])
    else:
        context["cart_size"] = 0
    context["search_form"] = SearchServiceForm()
    return context

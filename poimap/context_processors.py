from django.conf import settings

def poimap(request):
    context = {
        "POI_UNDER_CONTROL" : getattr(settings, "POI_UNDER_CONTROL", True)
    }
    return context

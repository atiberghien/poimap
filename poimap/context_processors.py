from django.conf import settings

def poimap(request):
    context = {
        "POI_UNDER_CONTROL" : getattr(settings, "POI_UNDER_CONTROL", True),
        "POI_CUSTOM_ITINERARY" : getattr(settings, "POI_CUSTOM_ITINERARY", True)
    }
    return context

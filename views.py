from django.shortcuts import render
from .models import Base

# Create your views here.

def test(request):
    bases = Base.objects.all()
    return render(request, 'itinerary.html',{'bases': bases})

# -*- coding: utf-8 -*-

from django import forms
from .models import POI

class CustomItineraryForm(forms.Form):
    start_point = forms.ModelChoiceField(queryset=POI.objects.filter(type__slug='etape'), empty_label=None, initial=POI.objects.filter(type__slug='etape').first())
    end_point = forms.ModelChoiceField(queryset=POI.objects.filter(type__slug='etape'), empty_label=POI.objects.filter(type__slug='etape').last())
    step = forms.IntegerField(label="Nombre de km/jour", widget=forms.NumberInput(attrs={'type':'range', 'min': 10, 'max': 40 , 'step':5}))

    class Media:
        css = {
            'all': ('rangeslider.js/dist/rangeslider.css',)
        }

        js = (
            'rangeslider.js/dist/rangeslider.min.js',
            'poimap/js/custom_itinerary.js',
        )

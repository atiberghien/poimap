# -*- coding: utf-8 -*-
from django.forms.widgets import HiddenInput
from django import forms
from .models import POI, POIRating

class CustomItineraryForm(forms.Form):
    start_point = forms.ModelChoiceField(label="Point de départ",queryset=POI.objects.all())
    end_point = forms.ModelChoiceField(label="Point d'arrivée", queryset=POI.objects.all())
    step = forms.IntegerField(label="Nombre de km/jour", widget=forms.NumberInput(attrs={'type':'range', 'min': 10, 'max': 40 , 'step':5}))

    def __init__(self, *args, **kwargs):
        super(CustomItineraryForm, self).__init__(*args, **kwargs)

        self.fields['start_point'].queryset = POI.objects.filter(starred=True)
        self.fields['end_point'].queryset = POI.objects.filter(starred=True)

        self.fields['start_point'].empty_label = "Sélectionnez un point de départ"
        self.fields['end_point'].empty_label = "Sélectionnez un point d'arrivée"

    class Media:
        css = {
            'all': ('rangeslider.js/dist/rangeslider.css',)
        }

        js = (
            'rangeslider.js/dist/rangeslider.min.js',
            'poimap/js/custom_itinerary.js',
        )

class POIRatingForm(forms.ModelForm):

    class Meta:
        model = POIRating
        fields = "__all__"
        widgets = {
            'poi': HiddenInput(),
            'user': HiddenInput(),
            'score': HiddenInput(),
        }

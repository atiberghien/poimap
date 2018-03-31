# -*- coding: utf-8 -*-
from dal import autocomplete

from django import forms
from .models import TimeSlot, Stop

class StopForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ('stop', 'hour')
        widgets = {
            'stop': autocomplete.ModelSelect2(url='stop-autocomplete')
        }


class SearchServiceForm1(forms.Form):
    departure = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete', attrs={'data-theme': "bootstrap4", 'data-placeholder' : u"Ville de départ"})
    )
    arrival = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete',
                                         forward=('departure',),
                                         attrs={
                                            'data-theme': "bootstrap4",
                                            'data-placeholder' : u"Ville d'arrivée"
                                         })
    )
    nb_passengers = forms.IntegerField(min_value=1)
    departure_date = forms.DateField()
    arrival_date = forms.DateField()

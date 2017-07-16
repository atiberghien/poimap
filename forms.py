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


class SearchRouteForm(forms.Form):
    departure = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete')
    )
    arrival = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete')
    )

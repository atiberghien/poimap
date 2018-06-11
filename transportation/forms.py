# -*- coding: utf-8 -*-
from django.utils.translation import ugettext, ugettext_lazy as _

from dal import autocomplete

from django import forms
from datetime import date
from .models import TimeSlot, Stop, Customer


class CustomerCreationForm(forms.ModelForm):

    error_messages = {
        'email_mismatch': _("The two password fields didn't match."),
    }
    email1 = forms.CharField(label=_("Email"), widget=forms.EmailInput)
    email2 = forms.CharField(label=_("Email confirmation"), widget=forms.EmailInput)

    class Meta:
        model = Customer
        fields = ("first_name", 'last_name', 'terms', 'privacy', 'optin')

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )
        return email2

    def save(self, commit=True):
        print "PLOP", commit
        try:
            customer = Customer.objects.get(email=self.cleaned_data["email1"])
        except Customer.DoesNotExist:
            customer = super(CustomerCreationForm, self).save(commit=False)
            customer.email = self.cleaned_data["email1"]
            if commit:
                customer.save() 
        return customer


class StopForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ('stop', 'hour')
        widgets = {
            'stop': autocomplete.ModelSelect2(url='stop-autocomplete')
        }


class SearchServiceForm(forms.Form):
    departure = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete', attrs={'data-theme': "bootstrap4",})
    )
    arrival = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete',
                                         forward=('departure',),
                                         attrs={
                                            'data-theme': "bootstrap4",
                                         })
    )
    nb_passengers = forms.IntegerField(min_value=1, initial=1)
    departure_date = forms.DateField()
    arrival_date = forms.DateField(required=False)

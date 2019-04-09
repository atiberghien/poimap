# -*- coding: utf-8 -*-
from django.utils.translation import ugettext, ugettext_lazy as _

from dal import autocomplete

from django import forms
from datetime import date
from .models import TimeSlot, Stop, Customer, Service, SMSNotification


class CustomerCreationForm(forms.ModelForm):

    error_messages = {
        'email_mismatch': _("The two password fields didn't match."),
    }
    email1 = forms.CharField(label=_("Email"), widget=forms.EmailInput)
    email2 = forms.CharField(label=_("Email confirmation"), widget=forms.EmailInput)

    class Meta:
        model = Customer
        fields = ("first_name", 'last_name', 'phone', 'sms_notif', 'terms', 'privacy', 'optin')

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )
        return email2
    
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if SMSNotification.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                self.error_messages['phone_already_exists'],
                code='phone_already_exists',
            )
        if len(phone) != 10 or phone[0:2] not in ['06', '07']:
            raise forms.ValidationError(
                self.error_messages['phone_wrong_format'],
                code='phone_wrong_format',
            )
        return "+33"+phone[1:]

    def save(self, commit=True):
        try:
            customer = Customer.objects.get(email=self.cleaned_data["email1"])
            customer.first_name = self.cleaned_data["first_name"]
            customer.last_name = self.cleaned_data["last_name"]
            customer.phone = self.cleaned_data["phone"]
            customer.sms_notif = self.cleaned_data["sms_notif"]
            customer.terms = self.cleaned_data["terms"]
            customer.privacy = self.cleaned_data["privacy"]
            customer.optin = self.cleaned_data["optin"]

            if not customer.sms_notif:
                try:
                    SMSNotification.objects.get(phone=customer.phone).delete()
                except:
                    pass

        except Customer.DoesNotExist:
            customer = super(CustomerCreationForm, self).save(commit=False)
            customer.email = self.cleaned_data["email1"]
            if customer.sms_notif:
                SMSNotification.objects.get_or_create(phone=customer.phone)
            
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
        widget=autocomplete.ModelSelect2(url='stop-autocomplete', attrs={'data-theme': "bootstrap4", 'data-placeholder' : u"  Ville de départ"})
    )
    arrival = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=autocomplete.ModelSelect2(url='stop-autocomplete',
                                         forward=('departure',),
                                         attrs={
                                            'data-theme': "bootstrap4",
                                            'data-placeholder' : u"  Ville d'arrivée"
                                         })
    )
    nb_passengers = forms.IntegerField(min_value=1, initial=1)
    departure_date = forms.DateField()
    arrival_date = forms.DateField(required=False)
    source = forms.CharField(widget=forms.HiddenInput(), initial="internal", required=False)


class SMSNotificationSubscriptionForm(forms.ModelForm):

    error_messages = {
        'phone_already_exists': _(u"Numéro déjà enregistré"),
        'phone_wrong_format' : _(u"Mauvais format de numéro de téléphone")
    }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if SMSNotification.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                self.error_messages['phone_already_exists'],
                code='phone_already_exists',
            )
        if len(phone) != 10 or phone[0:2] not in ['06', '07']:
            raise forms.ValidationError(
                self.error_messages['phone_wrong_format'],
                code='phone_wrong_format',
            )
        return "+33"+phone[1:]
    
    class Meta:
        model = SMSNotification
        fields = ('phone', )
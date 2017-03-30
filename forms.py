from django import forms
from hostings.models import Hostings, PaymentType
from itinerary.models import POIType


class HostingsForm(forms.ModelForm):
    class Meta:
        model = Hostings
        exclude = ['geo_coordinates', 'media']

    # hosting_type = forms.ModelChoiceField(queryset=POIType.objects.all(), label=u'Hosting type')
    name = forms.CharField(max_length=100, label=u'Name')
    # address = forms.CharField(max_length=250, label=u'Address')
    # zipcode = forms.CharField(max_length=50, label=u'Zipcode')
    # city = forms.CharField(max_length=300, label=u'City')
    phone = forms.CharField(max_length=15, required=False, label=u'Phone')
    fax = forms.CharField(max_length=15, required=False, label=u'Fax')
    email = forms.CharField(max_length=150, required=False, label=u'Email')
    web = forms.CharField(max_length=150, required=False, label=u'Web')
    # geo_coordinates = forms.PointField(required=False, label=u'Geo coordinates')
    # description = forms.CharField(required=False, label=u'Description')
    # media = forms.AdminImageFormField(required=False, label=u'Media')
    food = forms.BooleanField(initial=False, required=False, label=u'Food')
    picnic = forms.TypedChoiceField(initial=1, label=u'Picnic')
    picnic_price = forms.FloatField(required=False, label=u'Picnic price')
    car_parking = forms.BooleanField(initial=False, required=False, label=u'Car parking')
    cycle_garage = forms.BooleanField(initial=False, required=False, label=u'Cycle garage')
    stable = forms.BooleanField(initial=False, required=False, label=u'Stable')
    disabled_access = forms.BooleanField(initial=False, required=False, label=u'Disabled access')
    wifi = forms.BooleanField(initial=False, required=False, label=u'Wifi')
    pets = forms.BooleanField(initial=False, required=False, label=u'Pets')
    booking_phone_only = forms.BooleanField(initial=False, required=False, label=u'Booking phone only')
    food_shop = forms.BooleanField(initial=False, required=False, label=u'Food shop')
    washing_machine = forms.BooleanField(initial=False, required=False, label=u'Washing machine')
    tumble_drier = forms.BooleanField(initial=False, required=False, label=u'Tumble drier')
    sheet_renting = forms.BooleanField(initial=False, required=False, label=u'Sheet renting')
    pool = forms.BooleanField(initial=False, required=False, label=u'Pool')
    spa = forms.BooleanField(initial=False, required=False, label=u'Spa')
    jacuzzi = forms.BooleanField(initial=False, required=False, label=u'Jacuzzi')
    bivouac = forms.BooleanField(initial=False, required=False, label=u'Bivouac')
    min_price = forms.FloatField(required=False, label=u'Min price')
    max_price = forms.FloatField(required=False, label=u'Max price')
    accepted_payments = forms.ModelMultipleChoiceField(queryset=PaymentType.objects.all(), label=u'Accepted payments')

from django.contrib import admin
from easy_select2 import select2_modelform
from .models import Weather

WeatherForm = select2_modelform(Weather, attrs={'width': '250px'})

class WeatherAdmin(admin.ModelAdmin):
    form = WeatherForm
    list_display = ('poi', 'updated_at')

admin.site.register(Weather, WeatherAdmin)

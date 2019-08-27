from django import template

register = template.Library()

from transportation.models import TimeSlot
from time import strftime

@register.simple_tag
def stop_hour(service, stop):
    return TimeSlot.objects.get(service=service, stop=stop).hour.strftime("%H:%M")
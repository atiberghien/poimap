from datetime import datetime, date
from .models import Travel

def has_all_stop(timetable):
    for timeslot in timetable:
        if not timeslot.hour:
            return False
    return True


def increasing_hours(timetable):
    prev_slot = None
    for timeslot in timetable:
        if prev_slot and (prev_slot.hour >= timeslot.hour and not timeslot.is_next_day):
            return False
        prev_slot = timeslot
    return True


def get_timeslot_diff(timeslot1, timeslot2):
    min_time = datetime.combine(date.today(), timeslot1.hour)
    max_time = datetime.combine(date.today(), timeslot2.hour)
    return (max_time - min_time).total_seconds()


def get_total_time(timetable):
    return get_timeslot_diff(timetable[0], timetable[-1])


def get_max_wait(timetable):
    prev_slot = None
    max_wait = 0
    for timeslot in timetable:
        if prev_slot and prev_slot.stop.slug == timeslot.stop.slug:
            diff = get_timeslot_diff(prev_slot, timeslot)
            if diff > max_wait:
                max_wait = diff
        prev_slot = timeslot
    return max_wait


def get_route_length(timetable):
    prev_slot = None
    length = 0
    for timeslot in timetable:
        if prev_slot:
            try:
                edge = Travel.objects.get(stop1=prev_slot.stop, stop2=timeslot.stop)
                length += edge.distance
            except Travel.DoesNotExist:
                pass
        prev_slot = timeslot
    return length

def get_travel_price(timetable):
    prev_slot = None
    total_price = 0
    for timeslot in timetable:
        if prev_slot:
            try:
                edge = Travel.objects.get(stop1=prev_slot.stop, stop2=timeslot.stop)
                total_price += edge.price
            except Travel.DoesNotExist:
                pass
        prev_slot = timeslot
    return total_price



def timetable_sort_func(timetable):
    return (timetable[0].hour, get_total_time(timetable), get_max_wait(timetable), get_route_length(timetable))

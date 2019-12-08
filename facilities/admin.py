# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import DayOff
from datetime import datetime

class PerYearListFilter(admin.SimpleListFilter):
    title = "Par année"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        years = []
        for i in range(3):
            year = datetime.now().year + i
            years.append((year, year))
        
        return years

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        
        return queryset


@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ("date", 'desc')
    list_filter = (PerYearListFilter,)

    def get_actions(self, request):
        actions = super(DayOffAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        return False
# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class TransportationItineraryApp(CMSApp):
    name = _('Transportation itinerary')

    def get_urls(self, page=None, language=None, **kwargs):
        return ['transportation.itinerary_hook_urls']

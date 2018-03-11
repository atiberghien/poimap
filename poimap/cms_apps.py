# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.apphook_pool import apphook_pool
from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.urls import reverse
from .models import POI, POIListing, POI_LISTING_TEMPLATES

class StarredPOIMenu(CMSAttachMenu):

    name = _("Starred POI")

    def get_nodes(self, request):
        nodes = []
        level = 1
        for poi in POI.objects.filter(starred=True).order_by('name'):
            n = NavigationNode(poi.name, reverse("poi-detail", args=[poi.slug]), level)
            nodes.append(n)
            level += 1
        return nodes

menu_pool.register_menu(StarredPOIMenu)

@apphook_pool.register
class POIMapApp(CMSApp):
    name = _('POI Map')
    urls = ['poimap.urls']


@plugin_pool.register_plugin
class POIListingPlugin(CMSPluginBase):
    model = POIListing
    name = _("POI List Plugin")
    render_template = POI_LISTING_TEMPLATES[0][0]
    cache = False

    def render(self, context, instance, placeholder):
        context = super(POIListingPlugin, self).render(context, instance, placeholder)
        context["poi_type_slugs"] = instance.type_display.all().values_list('slug', flat=True)
        self.render_template = instance.template
        return context

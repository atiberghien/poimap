# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu
from django.core.urlresolvers import reverse
from .models import POI

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


class POIMapApp(CMSApp):
    name = _('POI Map')
    urls = ['poimap.urls']

apphook_pool.register(POIMapApp)

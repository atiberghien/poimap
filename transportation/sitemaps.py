from django.contrib.sitemaps import Sitemap

from .models import Bus, PartnerSearch


class BusSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Bus.objects.all()
    

class ItinerarySearchSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return PartnerSearch.objects.all().distinct('departure_stop', 'arrival_stop')
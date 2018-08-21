from django.contrib.sitemaps import Sitemap

from .models import Bus


class BusSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Bus.objects.all()
    
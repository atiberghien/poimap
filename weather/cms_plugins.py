from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import WeatherCMSPlugin

@plugin_pool.register_plugin
class WeatherPlugin(CMSPluginBase):
    model = WeatherCMSPlugin
    render_template = "weather/weather_plugin.html"
    cache = False

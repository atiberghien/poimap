
# INSTALL

Add 'poimap' and its dependencies in INSTALLED_APPS:

```
INSTALLED_APPS = [
    'polymorphic',
    ...
    'django.contrib.contenttypes',
    ...
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'treebeard',
    'fontawesome',
    'leaflet',
    'easy_thumbnails',
    "compressor",
    'bootstrap4',
    'poimap',
    ...
]
```

# SETTINGS

POI_UNDER_CONTROL(default:True) : POI layer will be gathered (or not) within a layer control

# URLS

```
urlpatterns = [
    ...
    url(r'^poimap/', include('poimap.urls')),
    url(r'^api/poimap/', include('poimap.api_urls')),
    ...
]
```

# MODEL
```
from poimap.models import POI


class MyModel(POI):
    pass
```

# ADMIN

Admin of a POI related model must look like :

```
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from poimap.admin import POIAdminForm
from .models import MyModel

class MyModelAdminForm(POIAdminForm):
    class Meta(POIAdminForm.Meta):
        model = MyModel

class MyModelAdmin(LeafletGeoAdmin):
    search_fields = ('name',)

    form = MyModelAdminForm

    fieldsets = (
        (None, {
            'fields': (('name', 'type'), 'description')
        }),
        (None, {
            'classes': ('address',),
            'fields': ('address',
                      ('zipcode', "city", 'country'))
        }),
        (None, {
            'classes': ('location',),
            'fields': ('geom',),
        }),
    )

admin.site.register(MyModel, MyModelAdmin)
```

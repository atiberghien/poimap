from setuptools import setup, find_packages

setup(name='poimap',
      version='1.1.0',
      description='Manage POI on a map',
      url='https://github.com/atiberghien/poimap',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
           'psycopg2',
           'Django',
           "django-compress",
           "django-sekizai",
           'django-autoslug',
           'django-countries',
           'djangorestframework',
           'djangorestframework-gis',
           'django-treebeard',
           'django-polymorphic',
           'django-polymorphic-tree',
           # 'django-filer',
           'easy-thumbnails',
           'django-leaflet',
           'django-fontawesome',
           'shapely'
      ],
      dependency_links=[
        "git+https://github.com/iplweb/django-autoslug-iplweb.git#egg=django-autoslug"
      ],
      zip_safe=False)

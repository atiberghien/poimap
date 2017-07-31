from setuptools import setup, find_packages

setup(name='poimap',
      version='0.1',
      description='Set POI on a map',
      url='https://github.com/atiberghien/poimap',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
           'psycopg2>=2.7.3',
           'Django>=1.11.3',
           "django-compress>=1.0.1",
           "django-sekizai>=0.10.0",
           'django-autoslug>=1.9.3',
           'django-countries>=4.6.1',
           'djangorestframework>=3.6.3',
           'djangorestframework-gis',
           'django-treebeard>=4.1.2',
           'django-polymorphic>=1.2',
           'django-polymorphic-tree',
           'django-filer>=1.2.7',
           'easy-thumbnails>=2.4.1',
           'django-leaflet>=0.22.0',
           'django-fontawesome>=0.3.1',
      ],
      zip_safe=False)

from setuptools import setup

setup(name='poimap',
      version='0.1',
      description='Set POI on a map',
      url='https://github.com/atiberghien/poimap',
      author='Alban Tiberghien',
      author_email='alban.tiberghien@gmail.com',
      license='MIT',
      packages=['poimap'],
      install_requires=[
           'Django>=1.11.3'
           'django_countries>=4.6.1',
           'djangorestframework>=3.6.3',
           'djangorestframework-gis',
           'django-treebeard>=4.1.2',
           'django-polymorphic>=1.2',
           'django-polymorphic-tree',
           'django-filer>=1.2.7',
           'easy-thumbnails>=2.4.1'
      ],
      zip_safe=False)

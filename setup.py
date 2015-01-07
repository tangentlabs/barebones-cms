from setuptools import setup

setup(name="barebones-cms",
      version="0.0.1",
      description="A very simple service orientated CMS for django",
      packages=['barebones_cms'],
      include_package_data=True,
      install_requires=[
        'django-mptt==0.6.1',
        'django==1.7',
        'django-extensions==1.4.9',
        'psycopg2==2.5.4',
        'Werkzeug==0.9.6',
        'ipdb==0.8',
      ])

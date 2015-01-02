from conf.default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cms_vagrant',
        'USER': 'cms_vagrant',
        'PASSWORD': 'vagrant',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEMPLATE_DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


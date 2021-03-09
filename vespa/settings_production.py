from .settings import *

import os

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

ALLOWED_HOSTS = [
    'stem-superwasp-live',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['POSTGRES_HOST'],
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
    }
}

STATIC_ROOT = '/opt/vespa/static'
STATIC_URL = '/'

CELERY_BROKER_URL = (
    f'amqp://{os.environ["CELERY_RABBITMQ_USER"]}:{os.environ["CELERY_RABBITMQ_PASS"]}'
    f'@{os.environ["CELERY_RABBITMQ_HOST"]}/{os.environ["CELERY_RABBITMQ_VHOST"]}'
)
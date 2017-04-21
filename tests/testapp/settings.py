# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import os

import django

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DATABASE_NAME", ":memory:"),
        'USER': os.environ.get("DATABASE_USER", ""),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD", ""),
    }
}

INSTALLED_APPS = [
    "tests.testapp"
]

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()

SECRET_KEY = "not needed"


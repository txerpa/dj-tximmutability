# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import os

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

DATABASES = {
    "default": {
        "ENGINE": os.environ.get(
            "DATABASE_ENGINE", "django.db.backends.sqlite3"
        ),
        "NAME": os.environ.get("DATABASE_NAME", ":memory:"),
        'USER': os.environ.get("DATABASE_USER", ""),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD", ""),
    }
}

INSTALLED_APPS = ['django.contrib.contenttypes', "tests.testapp"]

USE_I18N = True
USE_L10N = True

MIDDLEWARE_CLASSES = ()

SECRET_KEY = "not needed"

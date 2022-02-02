import os

import django
import pytest

from tests.testapp.constants import ModelState


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()


@pytest.fixture
def foo_instance():
    from tests.testapp.models import BaseModel

    return BaseModel.objects.create()


@pytest.fixture
def base_mutable_instance():
    from tests.testapp.models import BaseModel

    return BaseModel.objects.create(state=ModelState.MUTABLE_STATE)


@pytest.fixture
def base_immutable_instance():
    from tests.testapp.models import BaseModel

    return BaseModel.objects.create(state=ModelState.IMMUTABLE_STATE)

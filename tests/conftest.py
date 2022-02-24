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


def _base_immtable_instance(**kwargs):
    from tests.testapp.models import BaseModel

    fields = {"state": ModelState.IMMUTABLE_STATE}
    fields.update(kwargs)
    return BaseModel.objects.create(**fields)


@pytest.fixture
def base_immutable_instance():
    return _base_immtable_instance()


@pytest.fixture
def make_immutable_instance_record():
    def _make_immutable_instance_record(**kwargs):
        return _base_immtable_instance(**kwargs)

    return _make_immutable_instance_record

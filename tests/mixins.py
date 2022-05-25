from __future__ import absolute_import, unicode_literals

import pytest
from django.core.exceptions import ValidationError

from tests.testapp.models import ModelDepthFoo


class MixinTest:
    def delete_instance_when_model_is_immutable(self, immutable_instance):
        model = immutable_instance._meta.model
        assert 1 == len(model.objects.all())
        with pytest.raises(ValidationError):
            immutable_instance.delete()
        assert 1 == len(model.objects.all())

    def delete_instance_when_model_is_mutable(self, mutable_instance):
        model = mutable_instance._meta.model
        assert 1 == len(model.objects.all())
        mutable_instance.delete()
        assert 0 == len(model.objects.all())

    def update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        assert getattr(immutable_instance, field_name) != 'Foo'
        setattr(immutable_instance, field_name, "Foo")
        with expectation:
            immutable_instance.save()
        assert getattr(immutable_instance, field_name) == 'Foo'

    def update_field_when_model_is_mutable(self, mutable_instance, field_name):
        assert getattr(mutable_instance, field_name) != 'Foo'
        related_field_x = ModelDepthFoo()
        related_field_x.save()
        mutable_instance.related_field = related_field_x
        setattr(mutable_instance, field_name, "Foo")
        mutable_instance.save()
        assert getattr(mutable_instance, field_name) == 'Foo'
        assert getattr(mutable_instance, 'related_field') == related_field_x

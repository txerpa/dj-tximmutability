# coding=utf-8
from __future__ import absolute_import, unicode_literals

from contextlib import nullcontext as does_not_raise

import pytest
from django.core.exceptions import ValidationError

from tests.mixins import MixinTest
from tests.testapp.constants import ModelState
from tests.testapp.models import BaseMutabilityModel
from tximmutability.rule import MutabilityRule
from tximmutability.services import Or


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type_x,expectation",
    [
        (
            MutabilityRule(
                field_rule="state", values=(ModelState.MUTABLE_STATE,)
            ),
            does_not_raise(),
        ),
        (
            Or(
                MutabilityRule(
                    field_rule="state", values=(ModelState.MUTABLE_STATE,)
                )
            ),
            does_not_raise(),
        ),
        (Or(), pytest.raises(ValidationError)),
        ("a", pytest.raises(TypeError)),
        (1, pytest.raises(TypeError)),
        ([], pytest.raises(TypeError)),
        ((), pytest.raises(TypeError)),
    ],
)
def test_type_mutability_rules(base_mutable_instance, type_x, expectation):
    """
    Test valid types to pass to model.mutability_rules
    """
    mutability_rules = (type_x,)
    base_mutable_instance._mutability_rules = mutability_rules
    base_mutable_instance.name = "test"
    with expectation:
        base_mutable_instance.save()


@pytest.mark.django_db
class TestModelBasic(MixinTest):
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            error_message='Instance can not be %(action)s, immutable status',
            conditions=[],
            exclusion_conditions=[],
        ),
    )

    @pytest.fixture
    def mutable_instance(self, base_mutable_instance):
        base_mutable_instance._mutability_rules = self.mutability_rules
        return base_mutable_instance

    @pytest.fixture
    def immutable_instance(self, base_immutable_instance):
        base_immutable_instance._mutability_rules = self.mutability_rules
        return base_immutable_instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        self.delete_instance_when_model_is_immutable(immutable_instance)

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
            ("state", does_not_raise()),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )

    @pytest.mark.parametrize(
        "field_name,",
        ["description", "surname", "name", "state"],
    )
    def test_update_field_when_model_is_mutable(
        self, mutable_instance, field_name
    ):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)


@pytest.mark.django_db
class TestModelExcludeDelete(MixinTest):
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            error_message='Instance can not be %(action)s, immutable status',
            exclude_on_delete=True,
        ),
    )

    @pytest.fixture
    def mutable_instance(self, base_mutable_instance):
        base_mutable_instance._mutability_rules = self.mutability_rules
        return base_mutable_instance

    @pytest.fixture
    def immutable_instance(self, base_immutable_instance):
        base_immutable_instance._mutability_rules = self.mutability_rules
        return base_immutable_instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        """
        Check MutabilityRule.exclude_on_delete atribute for not met rule.
        """
        immutable_instance.delete()
        model = immutable_instance._meta.model
        assert 0 == len(model.objects.all())

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
            ("state", does_not_raise()),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )

    @pytest.mark.parametrize(
        "field_name,",
        ["description", "surname", "name", "state"],
    )
    def test_update_field_when_model_is_mutable(
        self, mutable_instance, field_name
    ):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)


@pytest.mark.django_db
class TestModelExcludeUpdate(MixinTest):
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            error_message='Instance can not be %(action)s, immutable status',
            exclude_on_update=True,
        ),
    )

    @pytest.fixture
    def mutable_instance(self, base_mutable_instance):
        base_mutable_instance._mutability_rules = self.mutability_rules
        return base_mutable_instance

    @pytest.fixture
    def immutable_instance(self, base_immutable_instance):
        base_immutable_instance._mutability_rules = self.mutability_rules
        return base_immutable_instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        self.delete_instance_when_model_is_immutable(immutable_instance)

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,",
        ["description", "surname", "name", "state"],
    )
    def test_update_field_when_model_is_mutable(
        self, mutable_instance, field_name
    ):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", does_not_raise()),
            ("name", does_not_raise()),
            ("state", does_not_raise()),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )

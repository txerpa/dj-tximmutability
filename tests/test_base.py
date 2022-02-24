# coding=utf-8
from __future__ import absolute_import, unicode_literals

from contextlib import nullcontext as does_not_raise

import pytest
from django.core.exceptions import ValidationError

from tests.mixins import MixinTest
from tests.testapp.constants import ModelState
from tests.testapp.models import BaseMutabilityModel
from tximmutability.exceptions import OrMutableException, RuleMutableException
from tximmutability.rule import MutabilityRule
from tximmutability.services import Or


@pytest.mark.django_db
@pytest.mark.parametrize(
    "args, kwargs, expectation, exc_val",
    [
        (
            ("", ("draft",)),
            {},
            pytest.raises(AssertionError),
            "MutabilityRule.field_rule can not be empty.",
        ),
        (
            ("estado", ["draft"]),
            {},
            pytest.raises(AssertionError),
            "MutabilityRule.values must have at least one element.",
        ),
        (
            ("estado", ()),
            {},
            pytest.raises(AssertionError),
            "MutabilityRule.values must have at least one element.",
        ),
    ],
)
def test_rule_initial_args_kwargs(args, kwargs, expectation, exc_val):
    """
    Test valid types to pass to model.mutability_rules
    """
    with expectation as excinfo:
        MutabilityRule(*args, **kwargs)
    if excinfo:
        assert exc_val in str(excinfo.value)


@pytest.mark.django_db
def test_error_code(base_immutable_instance):
    """
    Test valid types to pass to model.mutability_rules
    """
    error_code = "0001"
    base_immutable_instance._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
            error_code=error_code,
        ),
    )
    base_immutable_instance.name = "test"
    with pytest.raises(RuleMutableException) as excinfo:
        base_immutable_instance.save()

    assert error_code == excinfo.value.code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type_x,expectation",
    [
        (
            MutabilityRule(field_rule="state", values=(ModelState.MUTABLE_STATE,)),
            does_not_raise(),
        ),
        (
            Or(MutabilityRule(field_rule="state", values=(ModelState.MUTABLE_STATE,))),
            does_not_raise(),
        ),
        (Or(), pytest.raises(OrMutableException)),
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
            inst_conditions=[],
            inst_exclusion_conditions=[],
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
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
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
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
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
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
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

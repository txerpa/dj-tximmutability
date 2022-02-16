from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from tests.testapp.models import BaseModel, BaseMutabilityModel

# CONDITIONS


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__mutable_instance__condition_met(base_mutable_instance, condition_type):
    """
    Test - mutable_instance condition met. The rule will be executed.
    Updating not excluded fields, the rule will run succesfully
    (mutable_instance = rule.field_rule => accepted value.).
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',), inst_conditions=(condition_type,)
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules
    new_name_val = base_mutable_instance.name = "tx"
    new_surname_val = base_mutable_instance.surname = "python"
    base_mutable_instance.save()
    base_mutable_instance.refresh_from_db()
    assert base_mutable_instance.name == new_name_val
    assert base_mutable_instance.surname == new_surname_val


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__immutable_instance__condition_not_met(
    base_immutable_instance, condition_type
):
    """
    Test - immutability_instance condition not met.
    Updating not excluded fields will not execute the rule because the
    condition was not met.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',), inst_conditions=(condition_type,)
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    new_name_val = base_immutable_instance.name = "test"
    new_surname_val = base_immutable_instance.surname = "py"
    base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert base_immutable_instance.name == new_name_val
    assert base_immutable_instance.surname == new_surname_val


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__immutable_instance__condition_met__unfulfilled_rule(
    base_immutable_instance, condition_type
):
    """
    Test - immutability_instance condition met with unfulfilled rule.
    Updating not excluded fields and condition met, the rule will run with
    error.
    Instance will not be saved
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',), inst_conditions=(condition_type,)
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    base_immutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_immutable_instance.surname = "python"
    with pytest.raises(ValidationError):
        base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert base_immutable_instance.name == BaseMutabilityModel.DEFAULT_NAME
    assert base_immutable_instance.surname == BaseMutabilityModel.DEFAULT_SURNAME


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__immutable_instance__condition_met__fulfiled_rule(
    base_immutable_instance, condition_type
):
    """
    Test - immutability_instance condition met with fulfiled rule.
    Updating excluded fields (rule) and condition met, the rule will run
    successfully.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',), inst_conditions=(condition_type,)
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    new_val = base_immutable_instance.description = "tx-mutability"
    base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert base_immutable_instance.description == new_val


# MULTIPLE CONDITIONS


@pytest.mark.django_db
@mock.patch("tximmutability.rule.MutabilityRule.check_field_rule")
def test__immutable_instance__multi_condition__one_met(
    method_mock, base_immutable_instance
):
    """
    Test - immutability_instance , 2 conditions only one met.
    Updating excluded fields (rule) and condition met, the rule will run
    successfully.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_conditions=(BaseModel.condition_property, BaseModel.condition_func),
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    base_immutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_immutable_instance.surname = "fail"
    base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert not method_mock.called, 'a was called and should not have been'
    assert base_immutable_instance.name == BaseModel.ACCEPTED_VALUE_FUNC
    assert base_immutable_instance.surname == "fail"


@pytest.mark.django_db
@mock.patch("tximmutability.rule.MutabilityRule.check_field_rule")
def test__mutable_instance__multi_condition__one_met(
    method_mock, base_mutable_instance
):
    """
    Test - mutability_instance , 2 conditions only one met.
    Updating excluded fields (rule) and condition met, the rule will run
    successfully.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_conditions=(BaseModel.condition_property, BaseModel.condition_func),
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules
    base_mutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_mutable_instance.surname = "fail"
    base_mutable_instance.save()
    base_mutable_instance.refresh_from_db()
    assert not method_mock.called, 'a was called and should not have been'
    assert base_mutable_instance.name == BaseModel.ACCEPTED_VALUE_FUNC
    assert base_mutable_instance.surname == "fail"


# exclusion_conditions


@pytest.mark.django_db
@mock.patch("tximmutability.rule.MutabilityRule.check_field_rule")
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__mutable_instance__exclude_condition_met(
    method_mock, base_mutable_instance, condition_type
):
    """
    Test - mutable_instance exclude_condition met.
    Updating excluded fields (rule) and exclude_condition met, the rule will
    be excluded.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_exclusion_conditions=(condition_type,),
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules
    new_name_val = base_mutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    new_surname_val = base_mutable_instance.surname = "python"
    base_mutable_instance.save()
    base_mutable_instance.refresh_from_db()
    assert not method_mock.called, 'a was called and should not have been'
    assert base_mutable_instance.name == new_name_val
    assert base_mutable_instance.surname == new_surname_val


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__mutable_instance__exclude_condition_not_met(
    base_mutable_instance, condition_type
):
    """
    Test - mutable_instance exclude_condition not met.
    Updating excluded fields (rule) and exclude_condition not met, the rule
    will run successfully.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_exclusion_conditions=(condition_type,),
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules

    new_name_val = base_mutable_instance.name = "fail"
    new_surname_val = base_mutable_instance.surname = "fail"
    base_mutable_instance.save()
    base_mutable_instance.refresh_from_db()
    assert base_mutable_instance.name == new_name_val
    assert base_mutable_instance.surname == new_surname_val


@pytest.mark.django_db
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__immutable_instance__exclude_condition_not_met(
    base_immutable_instance, condition_type
):
    """
    Test - immutable_instance exclude_condition not met.
    Updating excluded fields (rule) and exclude_condition not met, the rule
    will run with error.
    Instance will not be saved.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_exclusion_conditions=(condition_type,),
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    base_immutable_instance.name = "test"
    base_immutable_instance.surname = "py"
    with pytest.raises(ValidationError):
        base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert base_immutable_instance.name == BaseMutabilityModel.DEFAULT_NAME
    assert base_immutable_instance.surname == BaseMutabilityModel.DEFAULT_SURNAME


@pytest.mark.django_db
@mock.patch("tximmutability.rule.MutabilityRule.check_field_rule")
@pytest.mark.parametrize(
    "condition_type,", [BaseModel.condition_property, BaseModel.condition_func]
)
def test__immutable_instance__exclude_condition_met(
    method_mock, base_immutable_instance, condition_type
):
    """
    Test - immutable_instance exclude_condition met.
    Updating excluded fields (rule) and exclude_condition met, the rule will
    be excluded.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_exclusion_conditions=(condition_type,),
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    new_name_val = base_immutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    new_surname_val = base_immutable_instance.surname = "python"
    base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert not method_mock.called, 'a was called and should not have been'
    assert base_immutable_instance.name == new_name_val
    assert base_immutable_instance.surname == new_surname_val


# MULTIPLE exclusion_conditions


@pytest.mark.django_db
@mock.patch("tximmutability.rule.MutabilityRule.check_field_rule")
def test__immutability_instance__multi_exclude_condition__one_met(
    method_mock, base_immutable_instance
):
    """
    Test - immutability_instance , 2 exclude_condition only one met.
    Updating excluded fields (rule) and a condition met, the rule will be
    excluded.
    """
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('description',),
            inst_conditions=(BaseModel.condition_property, BaseModel.condition_func),
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    base_immutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_immutable_instance.surname = "fail"
    base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert not method_mock.called, 'a was called and should not have been'
    assert base_immutable_instance.name == BaseModel.ACCEPTED_VALUE_FUNC
    assert base_immutable_instance.surname == "fail"

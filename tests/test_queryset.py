from contextlib import nullcontext as does_not_raise

import pytest

from tests.testapp.constants import ModelState
from tests.testapp.models import BaseModel, ModelDepthFoo
from tximmutability.exceptions import RuleMutableException
from tximmutability.rule import MutabilityRule


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, expectation",
    [("tx", pytest.raises(RuleMutableException)), ("_", does_not_raise())],
)
def test_queryset_conditions(make_immutable_instance_record, name, expectation):
    """
    This test check queryset update with `queryset_conditions` attribute.
    TestCase0 - all `queryset_conditions` met Rule is executed and fails (IMMUTABLE_STATE)
    TestCase1 - not all `queryset_conditions` met. Therefore, the Rule won't be executed.
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
            queryset_conditions=(BaseModel.objects.name_tx,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name=name)
    queryset = BaseModel.objects.all()
    with expectation:
        queryset.update(name="foo")


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["tx", "_"])
def test_queryset_conditions_on_single_instance(make_immutable_instance_record, name):
    """
    This test check that `queryset_conditions` attribute does not make any effect over single instance.
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
            queryset_conditions=(BaseModel.objects.name_tx,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name=name)
    instance = BaseModel.objects.first()
    instance.name = "foo"
    with pytest.raises(RuleMutableException):
        instance.save()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, expectation",
    [("tx", does_not_raise()), ("_", does_not_raise())],
)
def test_queryset_conditions_update_field_rule(
    make_immutable_instance_record, name, expectation
):
    """
    This test check that `queryset_conditions` attribute does not make any effect over 'field_rule' changes.
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
            queryset_conditions=(BaseModel.objects.name_tx,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name=name)
    queryset = BaseModel.objects.all()
    with expectation:
        queryset.update(state=ModelState.MUTABLE_STATE)


@pytest.mark.django_db
def test_update_queryset_force_mutability(make_immutable_instance_record):
    """
    This test check that `force mutability` attribute omit the rule, and therefore does not rise an error.
    Example: queryset.update(force_mutability=True, ...)
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name="tx")
    queryset = BaseModel.objects.all()
    with does_not_raise():
        queryset.update(force_mutability=True, name="foo1")


@pytest.mark.django_db
def test_bulk_update_queryset_force_mutability(make_immutable_instance_record):
    """
    This test check that `force mutability` attribute omit the rule, and therefore does not rise an error.
    Example: queryset.bulk_update(force_mutability=True, ...)
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            values=(ModelState.MUTABLE_STATE,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name="tx")

    objs = BaseModel.objects.all()
    for obj in objs:
        obj.name = 'foo1'

    with does_not_raise():
        BaseModel.objects.bulk_update(objs, ['name'], force_mutability=True)


@pytest.mark.django_db
def test_update_queryset_exclude_fields_fk(make_immutable_instance_record):
    """
    This test check that the fields (fk) inside `exclude_fields' will ignore the rule on mutation.
    """
    BaseModel._mutability_rules = (
        MutabilityRule(
            field_rule="state",
            exclude_fields=('related_field',),
            values=(ModelState.MUTABLE_STATE,),
        ),
    )
    for x in range(10):
        make_immutable_instance_record(name="tx")

    related_field = ModelDepthFoo()
    related_field.save()

    queryset = BaseModel.objects.all()
    with does_not_raise():
        queryset.update(related_field=related_field)

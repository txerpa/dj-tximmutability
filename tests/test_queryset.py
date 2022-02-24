from contextlib import nullcontext as does_not_raise

import pytest

from tests.testapp.constants import ModelState
from tests.testapp.models import BaseModel
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

import pytest
from django.core.exceptions import ValidationError

from tests.testapp.constants import ModelState
from tests.testapp.models import BaseModel, BaseMutabilityModel
from tximmutability.rule import MutabilityRule
from tximmutability.services import Or


@pytest.mark.django_db
def test__or_operator__fail(base_immutable_instance):
    """ """
    mutability_rules = (
        Or(
            MutabilityRule("state", values=(ModelState.MUTABLE_STATE,)),
            MutabilityRule(
                "name", values=("python",), exclude_fields=('description',)
            ),
        ),
    )
    base_immutable_instance._mutability_rules = mutability_rules
    base_immutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_immutable_instance.surname = "pyth"
    with pytest.raises(ValidationError):
        base_immutable_instance.save()
    base_immutable_instance.refresh_from_db()
    assert base_immutable_instance.name == BaseMutabilityModel.DEFAULT_NAME
    assert (
        base_immutable_instance.surname == BaseMutabilityModel.DEFAULT_SURNAME
    )


@pytest.mark.django_db
def test__or_operator__pass(base_mutable_instance):
    """ """
    mutability_rules = (
        Or(
            MutabilityRule("state", values=(ModelState.MUTABLE_STATE,)),
            MutabilityRule(
                "name", values=("python",), exclude_fields=('description',)
            ),
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules
    base_mutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_mutable_instance.surname = "pyth"
    base_mutable_instance.save()
    base_mutable_instance.refresh_from_db()
    assert base_mutable_instance.name == BaseModel.ACCEPTED_VALUE_FUNC
    assert base_mutable_instance.surname == "pyth"


@pytest.mark.django_db
def test__or_operator_inheritance(base_mutable_instance):
    """
    Test - Two or operator on inside other. Result successfully.
    """
    mutability_rules = (
        Or(
            Or(
                MutabilityRule("name", values=("pyt",)),
                MutabilityRule("state", values=(ModelState.MUTABLE_STATE,)),
            ),
            MutabilityRule("name", values=("python",)),
        ),
    )
    base_mutable_instance._mutability_rules = mutability_rules

    base_mutable_instance.name = BaseModel.ACCEPTED_VALUE_FUNC
    base_mutable_instance.surname = "pyth"
    base_mutable_instance.save()

    base_mutable_instance.refresh_from_db()
    assert base_mutable_instance.name == BaseModel.ACCEPTED_VALUE_FUNC
    assert base_mutable_instance.surname == "pyth"


@pytest.mark.django_db
def test__or_operator_with_external_rule__fail_rule(foo_instance):
    """
    Test - Or operator(2 rules) + rule. Or operator accepted but external rule
    fails.
    """
    mutability_rules = (
        Or(
            MutabilityRule("name", values=("pyt",)),
            MutabilityRule("state", values=(ModelState.MUTABLE_STATE,)),
        ),
        MutabilityRule("name", values=("python",)),
    )
    # name start as default value.
    foo_instance._mutability_rules = mutability_rules
    foo_instance.surname = "foo"
    with pytest.raises(ValidationError):
        foo_instance.save()

    foo_instance.refresh_from_db()
    assert foo_instance.name == BaseMutabilityModel.DEFAULT_NAME
    assert foo_instance.surname == BaseMutabilityModel.DEFAULT_SURNAME


@pytest.mark.django_db
def test__or_operator_with_external_rule__fail_or_operator(foo_instance):
    """
    Test - Or operator(2 rules) + rule. External rule accepted but Or operator
    fails.
    """
    mutability_rules = (
        Or(
            MutabilityRule("name", values=("pyt",)),
            MutabilityRule("state", values=("foo",)),
        ),
        MutabilityRule("name", values=(BaseMutabilityModel.DEFAULT_NAME,)),
    )
    # name start as default value.
    foo_instance._mutability_rules = mutability_rules
    foo_instance.surname = "foo"
    with pytest.raises(ValidationError):
        foo_instance.save()

    foo_instance.refresh_from_db()
    assert foo_instance.name == BaseMutabilityModel.DEFAULT_NAME
    assert foo_instance.surname == BaseMutabilityModel.DEFAULT_SURNAME

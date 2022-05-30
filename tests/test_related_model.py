from __future__ import absolute_import, unicode_literals

from contextlib import nullcontext as does_not_raise

import pytest
from django.core.exceptions import ValidationError

from tests.mixins import MixinTest
from tests.testapp.constants import ModelState
from tests.testapp.models import (
    BaseModel,
    BaseMutabilityModel,
    ModelDepthFoo,
    ModelFooReverse,
)


@pytest.mark.django_db
def test_queryset_conditions_update_field_rule(base_immutable_instance):
    """
    This test check that `queryset_conditions` attribute does not make any effect over 'field_rule' changes.
    """
    base_immutable_instance._mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            exclude_fields=('related_field',),
        ),
    )
    related_field_x = ModelDepthFoo()
    related_field_x.save()

    base_immutable_instance.related_field = related_field_x
    with does_not_raise():
        base_immutable_instance.save()


@pytest.mark.django_db
def test_rule_related_field_as_null():
    """
    This test check that `queryset_conditions` attribute does not make any effect over 'field_rule' changes.
    """
    mutable_instance = BaseModel.objects.create()
    mutable_instance._mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            field='related_field',
            values=(None,),
        ),
    )
    related_field_x = ModelDepthFoo()
    related_field_x.save()

    with does_not_raise():
        mutable_instance.related_field = related_field_x
        mutable_instance.save()


@pytest.mark.django_db
class TestRelation(MixinTest):
    model = BaseModel
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            field='related_field__state',
            exclude_fields=('description',),
            error_message='Instance can not be %(action)s, related field in '
            'immutable status',
        ),
    )

    @pytest.fixture
    def mutable_instance(self):
        instance = self.model.objects.create(
            state=ModelState.IMMUTABLE_STATE,
            related_field=ModelDepthFoo.objects.create(state=ModelState.MUTABLE_STATE),
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    @pytest.fixture
    def immutable_instance(self):
        instance = self.model.objects.create(
            state=ModelState.MUTABLE_STATE,
            related_field=ModelDepthFoo.objects.create(
                state=ModelState.IMMUTABLE_STATE
            ),
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        self.delete_instance_when_model_is_immutable(immutable_instance)

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,",
        [
            "description",
            "surname",
            "name",
        ],
    )
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )


@pytest.mark.django_db
class TestMultiForwardRel(MixinTest):
    model = BaseModel
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            field='related_field__related_field__state',
            exclude_fields=('description',),
        ),
    )

    @pytest.fixture
    def mutable_instance(self):
        instance = self.model.objects.create(
            state=ModelState.IMMUTABLE_STATE,
            related_field=ModelDepthFoo.objects.create(
                state=ModelState.IMMUTABLE_STATE,
                related_field=ModelDepthFoo.objects.create(
                    state=ModelState.MUTABLE_STATE,
                ),
            ),
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    @pytest.fixture
    def immutable_instance(self):
        instance = self.model.objects.create(
            state=ModelState.MUTABLE_STATE,
            related_field=ModelDepthFoo.objects.create(
                state=ModelState.MUTABLE_STATE,
                related_field=ModelDepthFoo.objects.create(
                    state=ModelState.IMMUTABLE_STATE,
                ),
            ),
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        self.delete_instance_when_model_is_immutable(immutable_instance)

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,",
        [
            "description",
            "surname",
            "name",
        ],
    )
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )


@pytest.mark.django_db
class TestReverseRelation(MixinTest):
    model = BaseModel
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            field='modelfooreverse__state', exclude_fields=('description',)
        ),
    )

    @pytest.fixture
    def mutable_instance(self):
        instance = self.model.objects.create()
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    @pytest.fixture
    def immutable_instance(self):
        instance = self.model.objects.create()
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.IMMUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=instance, state=ModelState.MUTABLE_STATE
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        self.delete_instance_when_model_is_immutable(immutable_instance)

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        self.delete_instance_when_model_is_mutable(mutable_instance)

    @pytest.mark.parametrize(
        "field_name,",
        [
            "description",
            "surname",
            "name",
        ],
    )
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )


@pytest.mark.django_db
class TestMultiReverseRelation(MixinTest):
    model = BaseModel
    mutability_rules = (
        BaseMutabilityModel.get_mutability_rule(
            field='basemodel__modelfooreverse__state',
            exclude_fields=('description',),
        ),
    )

    @pytest.fixture
    def mutable_instance(self):
        """
        ModelFooReverse _____ level1_1  _______ instance
        ModelFooReverse __/                 /
                                           /
        ModelFooReverse _____ level1_2  __/
        ModelFooReverse __/
        """
        instance = self.model.objects.create()
        level1_1 = self.model.objects.create(
            own_related_field=instance, state=ModelState.IMMUTABLE_STATE
        )
        level1_2 = self.model.objects.create(
            own_related_field=instance, state=ModelState.IMMUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_1, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_1, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_2, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_2, state=ModelState.MUTABLE_STATE
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    @pytest.fixture
    def immutable_instance(self):
        """
        ModelFooReverse _____ level1_1  _______ instance
        ModelFooReverse __/                 /
                                           /
        ModelFooReverse _____ level1_2  __/
        ModelFooReverse __/
        """
        instance = self.model.objects.create()
        level1_1 = self.model.objects.create(
            own_related_field=instance, state=ModelState.MUTABLE_STATE
        )
        level1_2 = self.model.objects.create(
            own_related_field=instance, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_1, state=ModelState.IMMUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_1, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_2, state=ModelState.MUTABLE_STATE
        )
        ModelFooReverse.objects.create(
            related_field=level1_2, state=ModelState.MUTABLE_STATE
        )
        instance._mutability_rules = self.mutability_rules
        return instance

    def test_delete_instance_when_model_is_immutable(self, immutable_instance):
        assert 3 == len(self.model.objects.all())
        with pytest.raises(ValidationError):
            immutable_instance.delete()
        assert 3 == len(self.model.objects.all())

    def test_delete_instance_when_model_is_mutable(self, mutable_instance):
        assert 3 == len(self.model.objects.all())
        mutable_instance.delete()
        assert 0 == len(self.model.objects.all())

    @pytest.mark.parametrize(
        "field_name,",
        [
            "description",
            "surname",
            "name",
        ],
    )
    def test_update_field_when_model_is_mutable(self, mutable_instance, field_name):
        self.update_field_when_model_is_mutable(mutable_instance, field_name)

    @pytest.mark.parametrize(
        "field_name,expectation",
        [
            ("description", does_not_raise()),
            ("surname", pytest.raises(ValidationError)),
            ("name", pytest.raises(ValidationError)),
        ],
    )
    def test_update_field_when_model_is_immutable(
        self, immutable_instance, field_name, expectation
    ):
        self.update_field_when_model_is_immutable(
            immutable_instance, field_name, expectation
        )

# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.db import models

from tests.testapp.constants import ModelState
from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule


class AbstractImmutableModel(MutableModel):
    name = models.CharField(
        null=False, max_length=50, default='Immutable Model'
    )
    state = models.CharField(max_length=50, default=ModelState.IMMUTABLE_STATE)

    @staticmethod
    def get_mutability_rule(**kwargs):
        field = kwargs.pop('field', None)
        field_name = 'state' if field is None else field
        return MutabilityRule(
            field_name, values=(ModelState.MUTABLE_STATE,), **kwargs
        )

    class Meta:
        abstract = True

    def saved_value(self, field):
        # self.refresh_from_db()
        hints = {'instance': self}
        db_instance_qs = (
            self.__class__._base_manager.db_manager(hints=hints)
            .filter(pk=self.pk)
            .only(field)
        )
        return getattr(db_instance_qs.get(), 'state')


class BaseImmutableModel(AbstractImmutableModel):
    description = models.CharField(null=True, max_length=250)
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            exclude_fields=('description',),
            error_message='Instance can not be %(action)s, immutable status',
        ),
    )


class ImmutableModelAllowDelete(AbstractImmutableModel):
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(exclude_on_delete=True),
    )


class ImmutableModelAllowUpdate(AbstractImmutableModel):
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(exclude_on_update=True),
    )


class ImmutableRelationModel(AbstractImmutableModel):
    related_field = models.ForeignKey(
        'BaseImmutableModel', on_delete=models.CASCADE, null=True, blank=True
    )
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            field='related_field__state'
        ),
    )


class ImmutableMultiForwardRelModel(AbstractImmutableModel):
    related_field = models.ForeignKey(
        'ModelWithRelation', on_delete=models.CASCADE, null=True, blank=True
    )
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            field='related_field__related_field__state'
        ),
    )


class ImmutableReverseRelationModel(AbstractImmutableModel):
    related_field = models.ForeignKey(
        'ImmutableMultiReverseRelModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            field='modelwithrelation__state'
        ),
    )


class ImmutableMultiReverseRelModel(AbstractImmutableModel):
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            field='immutablereverserelationmodel__' 'modelwithrelation__state'
        ),
    )


class ImmutableMultiMixRelModel(AbstractImmutableModel):
    related_field = models.ForeignKey(
        'BaseImmutableModel', on_delete=models.CASCADE, null=True, blank=True
    )
    mutability_rules = (
        AbstractImmutableModel.get_mutability_rule(
            field='related_field__immutablerelationmodel__state'
        ),
        AbstractImmutableModel.get_mutability_rule(
            field='modelwithrelation__related_field__state'
        ),
    )


class ModelWithRelation(AbstractImmutableModel):
    related_field = models.ForeignKey(
        'ImmutableReverseRelationModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    related_field2 = models.ForeignKey(
        'ImmutableMultiMixRelModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

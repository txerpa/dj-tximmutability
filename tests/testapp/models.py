# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.db import models

from tests.testapp.constants import ModelState
from tximmutability.models import ImmutableModel
from tximmutability.rule import ImmutabilityRule


class AbstractImmutableModel(ImmutableModel):
    name = models.CharField(null=False, max_length=50, default='Immutable Model')
    state = models.CharField(max_length=50, default=ModelState.IMMUTABLE_STATE)

    @staticmethod
    def get_immutability_rule(**kwargs):
        field = kwargs.pop('field', None)
        field_name = 'state' if field is None else field
        return ImmutabilityRule(field_name, mutable_values=(ModelState.MUTABLE_STATE,), **kwargs)

    class Meta:
        abstract = True


class BaseImmutableModel(AbstractImmutableModel):
    description = models.CharField(null=True, max_length=250)
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(mutable_fields=('description',),
                                                     error_message='No se puede {action}, estado es inmutable'),
    )


class ImmutableModelAllowDelete(AbstractImmutableModel):
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(allow_delete=True),
    )


class ImmutableModelAllowUpdate(AbstractImmutableModel):
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(allow_update=True),
    )


class ImmutableRelationModel(AbstractImmutableModel):
    related_field = models.ForeignKey('BaseImmutableModel', null=True, blank=True)
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(field='related_field__state'),
    )


class ImmutableMultiForwardRelModel(AbstractImmutableModel):
    related_field = models.ForeignKey('ModelWithRelation', null=True, blank=True)
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(field='related_field__related_field__state'),
    )


class ImmutableReverseRelationModel(AbstractImmutableModel):
    related_field = models.ForeignKey('ImmutableMultiReverseRelModel', null=True, blank=True)
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(field='modelwithrelation__state'),
    )


class ImmutableMultiReverseRelModel(AbstractImmutableModel):
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(field='immutablereverserelationmodel__'
                                                           'modelwithrelation__state'),
    )


class ImmutableMultiMixRelModel(AbstractImmutableModel):
    related_field = models.ForeignKey('BaseImmutableModel', null=True, blank=True)
    immutability_rules = (
        AbstractImmutableModel.get_immutability_rule(field='related_field__immutablerelationmodel__state'),
        AbstractImmutableModel.get_immutability_rule(field='modelwithrelation__related_field__state')
    )


class ModelWithRelation(AbstractImmutableModel):
    related_field = models.ForeignKey('ImmutableReverseRelationModel', null=True, blank=True)
    related_field2 = models.ForeignKey('ImmutableMultiMixRelModel', null=True, blank=True)


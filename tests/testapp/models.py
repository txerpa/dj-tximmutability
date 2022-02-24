from __future__ import absolute_import, unicode_literals

from django.db import models

from tests.testapp.constants import ModelState
from tximmutability.models import MutableModel, MutableQuerySet
from tximmutability.rule import MutabilityRule


class BaseAbsModel(MutableModel):
    class Meta:
        abstract = True

    @staticmethod
    def get_mutability_rule(**kwargs):
        field = kwargs.pop('field', None)
        field_name = 'state' if field is None else field
        values = kwargs.pop('values', (ModelState.MUTABLE_STATE,))
        return MutabilityRule(field_name, values=values, **kwargs)

    def saved_value(self, field):
        hints = {'instance': self}
        db_instance_qs = (
            self.__class__._base_manager.db_manager(hints=hints)
            .filter(pk=self.pk)
            .only(field)
        )
        return getattr(db_instance_qs.get(), 'state')


class ModelDepthFoo(BaseAbsModel):
    name = models.CharField(null=False, max_length=50, default='Initial Foo')
    state = models.CharField(max_length=50, default=ModelState.MUTABLE_STATE)
    related_field = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True
    )

    _mutability_rules = (BaseAbsModel.get_mutability_rule(),)


class InvoiceQuerySet(MutableQuerySet, models.QuerySet):
    def name_tx(self):
        return self.count() == self.filter(name="tx").count()


class BaseMutabilityModel(BaseAbsModel):
    DEFAULT_NAME = "Mutability name"
    DEFAULT_SURNAME = "Mutability surname"

    name = models.CharField(null=False, max_length=50, default=DEFAULT_NAME)
    surname = models.CharField(null=False, max_length=100, default=DEFAULT_SURNAME)
    state = models.CharField(max_length=50, default=ModelState.IMMUTABLE_STATE)
    description = models.CharField(null=True, max_length=250)
    related_field = models.ForeignKey(
        ModelDepthFoo, on_delete=models.CASCADE, null=True, blank=True
    )
    own_related_field = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    objects = InvoiceQuerySet.as_manager()

    class Meta:
        abstract = True


class BaseModel(BaseMutabilityModel):
    ACCEPTED_VALUE_FUNC = "tx"

    def condition_property(self):
        return len(self.surname) > 5

    def condition_func(self):
        return self.name == self.ACCEPTED_VALUE_FUNC


class ModelFooReverse(BaseAbsModel):
    name = models.CharField(null=False, max_length=50, default='Immutable Model')
    state = models.CharField(max_length=50, default=ModelState.IMMUTABLE_STATE)
    related_field = models.ForeignKey(
        "BaseModel", on_delete=models.CASCADE, null=True, blank=True
    )

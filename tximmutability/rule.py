# coding=utf-8
from __future__ import absolute_import, unicode_literals

import logging
from typing import Tuple

from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignObjectRel, RelatedField
from django.utils.translation import gettext as _

logger = logging.getLogger('txmutability')


class MutabilityRule:
    """
    This class serves to define the rule when an model is mutable.
    To define mutability rule it is mandatory to define "field_rule"
    of the model from which depend model mutability.
    To define relation field use '__' as separator in "field_rule"

    Once, "field_rule" is defined, model becomes immutable if the rule is not
    fulfilled (you can not update
    it or delete it).

    Attributes
    ----------
        field_rule <String>: field mutability effects.
        values <Tuple>: Tuple of values to establish when the model will be
        mutable.
        exclude_fields <Tuple>: set of fields names to exclude for this rule.
        exclude_on_create <Bool>: To exclude this rule on create set <True>,
            otherwise <False>. Default True
        exclude_on_update <Bool>: To exclude this rule on update set <True>,
            otherwise <False>. Default False
        exclude_on_delete <Bool>: To exclude this rule on delete set <True>,
            otherwise <False>. Default False
        condition <Tuple>. Tuple of Strings of instance method/property that
            return <Bool>. Methods to check before applying this rule.
        exclusion_conditions <Tuple>. Tuple of Strings of instance
            method/property that return <Bool>. Methods to check before
            applying this rule.
        error_message  <String>: Message passed on raise.
        error_code <String>: Error code for ValidationError in case rule fails.

    Examples:
        - Only invoice note can be changed if invoice is not in draft state.
        MutabilityRule('state', values=('draft',), exclude_fields=('note',))
        - Entry can not be deleted (but can be updated) if related invoice is
            validated
        MutabilityRule('invoice__state', values=('draft',),
            exclude_on_update=True)
        - Invoice line cannot be updated or deleted nor new line can be added
            if invoice is not in draft or budget state
        MutabilityRule('invoice__state', values=('draft', 'budget'),
        exclude_on_create=False)
    """

    def __init__(
        self,
        field_rule,
        values: Tuple = (),
        exclude_fields: Tuple = (),
        exclude_on_create=True,
        exclude_on_update=False,
        exclude_on_delete=False,
        inst_conditions: Tuple = (),
        inst_exclusion_conditions: Tuple = (),
        queryset_conditions: Tuple = (),
        queryset_exclusion_conditions: Tuple = (),
        error_message=None,
        error_code=None,
    ) -> None:
        self.field_rule = field_rule
        self.values = values
        self.exclude_fields = exclude_fields or ()
        # Actions mutable by.
        self.exclude_on_create = exclude_on_create
        self.exclude_on_update = exclude_on_update
        self.exclude_on_delete = exclude_on_delete
        # Conditions attr
        self.inst_conditions = inst_conditions or ()
        self.inst_exclusion_conditions = inst_exclusion_conditions or ()
        self.queryset_conditions = queryset_conditions or ()
        self.queryset_exclusion_conditions = queryset_exclusion_conditions or ()
        # Errors attr
        self.error_message = error_message
        self.error_code = error_code

    def get_error(self, action):
        message = (
            self.error_message.format(
                action=action, field_rule=self.field_rule, accepted_values=self.values
            )
            if self.error_message
            else _(
                f"Model rule does not hold for action {action}, field "
                f"\"{self.field_rule}\" must have as values {self.values}"
            )
        )
        return ValidationError(message, code=self.error_code)

    def is_mutable(self, obj):
        """
        Check if model obj is in mutable state.
        Model obj is in mutable state if field defined by rule has
        one of the values defined in values. If field is relation check
        if relation is mutable
        :param model_instance: TxerpadBase
        :param field_parts: name of the field or related object field
        (e.g 'state' or 'invoice__state')
        :return: bool
        """
        self.obj = obj
        self.is_queryset = isinstance(obj, QuerySet)

        if not self._all_conditions_met():
            # Not all conditions met. It does not continue checking this
            # rule.
            return True

        if self._any_conditions_met():
            # Some conditions met from exclude_conditions. It does not
            # continue checking this rule.
            return True
        if self.is_queryset:
            return all(map(lambda instance: self.check_field_rule(instance), self.obj))
        else:
            return self.check_field_rule(obj)

    def check_field_rule(self, model_instance, field_parts=None):
        field_parts = field_parts or self.field_rule.split('__')
        opts = model_instance._meta

        # walk relationships
        for field_name in field_parts:
            try:
                rel = opts.get_field(field_name)
            except FieldDoesNotExist:
                logger.warning(_(f"Field does not exist - {field_name}"))
                return True
            if isinstance(rel, (RelatedField, ForeignObjectRel)):
                # field is forward or reverse relation
                rel_parts = field_parts[field_parts.index(field_name) + 1 :]
                if isinstance(rel, ForeignObjectRel):
                    field_name = rel.get_accessor_name()
                field_val = getattr(model_instance, field_name)
                return self._is_mutable_relation(rel, field_val, rel_parts)
            else:
                # field is model attribute
                field_val = model_instance.saved_value(field_name)
                # field_val = getattr(model_instance, field_name, None)
                return field_val in self.values

    def _is_mutable_relation(self, relation, value, rel_parts):
        """
        Relation is mutable if related object(s) has mutable state.
        If related object is not defined relation is mutable by default.
        If there are more related objects (relation is many_to_many or
         one_to_many)
        relation is mutable only if all related objects are mutable
        :param relation: ForeignObjectRel|RelatedField
        :param value: related object
        :param rel_parts: name of the field or related object field
        :return: bool
        """
        if not rel_parts:
            return value in self.values
        if not value:
            return True
        if relation.many_to_many or relation.one_to_many:
            for related_object in value.all():
                if not self.check_field_rule(related_object, field_parts=rel_parts):
                    return False
            return True
        else:
            return self.check_field_rule(value, field_parts=rel_parts)

    def _check_inst_codition(self, condition):
        return condition(self.obj)

    def _check_query_codition(self, condition):
        return self.obj.__getattribute__(condition.__name__)

    def _all_conditions_met(self):
        """
        Check if all conditions have been met
        """
        if self.is_queryset:
            return all(
                map(
                    lambda condition: self._check_query_codition(condition),
                    self.queryset_conditions,
                )
            )
        else:
            return all(
                map(
                    lambda condition: self._check_inst_codition(condition),
                    self.inst_conditions,
                )
            )

    def _any_conditions_met(self):
        """
        Check if all conditions have been met
        """
        if self.is_queryset:
            return any(
                map(
                    lambda condition: self._check_query_codition(condition),
                    self.queryset_exclusion_conditions,
                )
            )
        else:
            return any(
                map(
                    lambda condition: self._check_inst_codition(condition),
                    self.inst_exclusion_conditions,
                )
            )

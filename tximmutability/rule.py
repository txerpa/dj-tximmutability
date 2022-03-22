# coding=utf-8
from __future__ import absolute_import, unicode_literals

import logging
from typing import NoReturn, Tuple

from django.core.exceptions import FieldDoesNotExist
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignObjectRel, RelatedField
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy, ngettext

from .exceptions import RuleMutableException

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
        inst_conditions <Tuple>: Tuple of instance methods that return <Bool>.
            Methods to check before applying this rule.
        inst_exclusion_conditions <Tuple>. Tuple of instance methods that
            return <Bool>. Methods to check before applying this rule.
        queryset_conditions <Tuple>: Tuple of modelmanager methods that return <Bool>.
            Methods to check before applying this rule.
        queryset_exclusion_conditions <Tuple>: Tuple of modelmanager methods that
            return <Bool>. Methods to check before applying this rule.
        error_message  <String>: Message passed on raise.
        error_code <String>: Error code for ValidationError in case rule fails.

    """

    def __init__(
        self,
        field_rule: str,
        values: Tuple,
        exclude_fields: Tuple = None,
        exclude_on_create: bool = True,
        exclude_on_update: bool = False,
        exclude_on_delete: bool = False,
        inst_conditions: Tuple = None,
        inst_exclusion_conditions: Tuple = None,
        queryset_conditions: Tuple = None,
        queryset_exclusion_conditions: Tuple = None,
        error_message: str = None,
        error_code: str = None,
    ) -> NoReturn:
        assert bool(field_rule), "MutabilityRule.field_rule can not be empty."
        assert (
            isinstance(values, Tuple) and len(values) > 0
        ), "MutabilityRule.values must have at least one element."

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

    def __str__(self):
        return f"{self.__class__.__name__}[{self.field_rule}={self.values}]"

    def get_error(self, action):
        if self.error_message:
            message = format_lazy(
                self.error_message,
                action=action,
                field_rule=self.field_rule,
                values=",".join(self.values),
            )
        else:
            base_text = ngettext(
                "The model rule does not hold for action {action}, field \"{field_rule}\" must have as value \"{values}\".",
                "The model rule does not hold for action {action}, field \"{field_rule}\" must have as values \"{values}\".",
                len(self.values),
            )
            message = format_lazy(
                base_text,
                action=action,
                field_rule=self.field_rule,
                values=",".join(self.values),
            )

        return RuleMutableException(message, code=self.error_code)

    def is_mutable(self, obj, action):
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
            return True, None

        if self._any_conditions_met():
            # Some conditions met from exclude_conditions. It does not
            # continue checking this rule.
            return True, None
        if self.is_queryset:
            # return all(map(lambda instance: self.check_field_rule(instance), self.obj))
            failed_instances = []
            for instance in self.obj:
                if not self.check_field_rule(instance):
                    logger.warning(
                        f"Instance {instance}-pk[{instance.pk}] is not mutable for [{action}] action. {self.__str__()}"
                    )
                    failed_instances.append(instance)
            is_mutable = False if failed_instances else True
            return is_mutable, failed_instances
        else:
            return self.check_field_rule(obj), None

    def check_field_rule(self, model_instance, field_parts=None):
        field_parts = field_parts or self.field_rule.split('__')
        opts = model_instance._meta

        # walk relationships
        for field_name in field_parts:
            try:
                rel = opts.get_field(field_name)
            except FieldDoesNotExist:
                logger.warning(gettext_lazy(f"Field does not exist - {field_name}"))
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
        return self.obj.__getattribute__(condition.__name__)()

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
        Check if any conditions have been met
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

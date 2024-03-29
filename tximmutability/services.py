from __future__ import absolute_import, unicode_literals

from abc import ABC, abstractmethod

from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy

from .exceptions import OrMutableException
from .rule import MutabilityRule


class BaseMutableModelAction(ABC):
    """
    Action performed on the instance of an mutable model.
    To implement concrete MutableModelAction it is obligatory to define
    action name and to implement is_allowed method

    To validate action against immutability rules call validate(rules) method
    """

    def __init__(self, instance_or_queryset):
        assert isinstance(instance_or_queryset, QuerySet) or isinstance(
            instance_or_queryset.__class__, ModelBase
        ), "Obj must be an instance of QuerySet or ModelBase"

        self.queryset = None
        self.model_instance = None
        if isinstance(instance_or_queryset, QuerySet):
            self.queryset = instance_or_queryset
            self.model_name = self.queryset.model.__name__
        else:
            self.model_instance = instance_or_queryset
            self.model_name = self.model_instance.__class__.__name__

    def check_types(self, model_instance, mutability_rules):
        if not isinstance(mutability_rules, (tuple, list)):
            raise TypeError(
                gettext_lazy(
                    '%s.mutability_rules attribute must be a list.' % self.model_name
                )
            )
        for x in filter(lambda e: isinstance(e, Or), mutability_rules):
            self.check_types(model_instance, x.rules_or_conditions)
        if any(
            map(
                lambda e: not isinstance(e, (MutabilityRule, Or)),
                mutability_rules,
            )
        ):
            raise TypeError(
                gettext_lazy(
                    '%s.mutability_rule attribute must be an instance of '
                    '\"MutabilityRule\".' % self.model_name
                )
            )

    def validate(self, rules_and_coditions):
        """
        :param: MutableModelAction []
        :raise: ValidationError
        """
        self.check_types(self.model_instance, rules_and_coditions)
        for rule_or_condition in rules_and_coditions:
            if not self.rule_or_condition_met(rule_or_condition):
                raise rule_or_condition.get_error(self.action)

    def rule_or_condition_met(self, rule_or_condition, or_obj=None):
        if isinstance(rule_or_condition, Or):
            or_obj = rule_or_condition
            or_obj.clear()
            for r__or__orc in or_obj.rules_or_conditions:
                if self.rule_or_condition_met(r__or__orc, or_obj=or_obj):
                    return True
                else:
                    or_obj.errors.append(r__or__orc.get_error(self.action))
        else:
            return self.is_rule_met(rule_or_condition, or_obj=or_obj)
        return False

    @abstractmethod
    def is_rule_met(self, rule, or_obj=None):
        """
        Check if the action on the concrete item is allowed by the given rule
        :param rule: ImmutabilityRule
        :return: bool
        """
        pass


class BaseMutableModelUpdate(BaseMutableModelAction):
    action = gettext_lazy('update')

    def __init__(self, instance_or_queryset, update_fields=None):
        self.errors = {}
        super(BaseMutableModelUpdate, self).__init__(instance_or_queryset)
        assert (
            bool(self.queryset) and bool(update_fields) or not bool(self.queryset)
        ), "\"update_fields\" must be set if \"queryset\" is passed."
        self.fields_names = (
            update_fields or self.model_instance.tracker.changed().keys()
        )

    def _get_fields_names_to_exclude(self, instance, rule):
        """
        map fk field to column db, ex: django => book.autor || DB --> book.autor_id
        """
        fields_names = (
            {f for f in rule.exclude_fields}
            if bool(self.queryset)
            else {instance._meta.get_field(f).column for f in rule.exclude_fields}
        )
        fr = rule.field_rule
        if "__" not in fr:  # is not field related to fk field.
            fields_names.add(
                fr if bool(self.queryset) else instance._meta.get_field(fr).column
            )
        return fields_names

    def is_rule_met(self, rule, or_obj=None):
        """
        Update of the instance field for the given rule is allowed if one of
        the following cases is fulfill:
        - update is allowed by rule
        - rule is defined for the field we want to update
        - field is defined as one of mutable fields in rule
        - Model instance is in mutable state
        :param rule: ImmutabilityRule
        :return: bool
        """
        if rule.exclude_on_update:
            return True

        # Todo iterar todos
        instance = self.model_instance or self.queryset[0]

        exclude_db_column_names = self._get_fields_names_to_exclude(instance, rule)
        # Clean fields to check.
        fields_to_check = self.fields_names - exclude_db_column_names
        result = True
        if fields_to_check:
            result, failed_instances = rule.is_mutable(
                self.model_instance or self.queryset, self.action
            )
        return result


class BaseMutableModelDelete(BaseMutableModelAction):
    action = gettext_lazy('delete')

    def is_rule_met(self, rule, or_obj=None):
        """
        Delete of the instance is allowed if rule by self allow delete or
        if instance is in mutable state
        """
        if rule.exclude_on_delete:
            return True
        result, _ = rule.is_mutable(self.model_instance or self.queryset, self.action)
        return result


class BaseMutableModelCreate(BaseMutableModelAction):
    action = gettext_lazy('create')

    def is_rule_met(self, rule, or_obj=None):
        """
        Create is allowed if rule byself allow creation or if model is in
        mutable state
        """

        if rule.exclude_on_create:
            return True
        result, _ = rule.is_mutable(self.model_instance or self.queryset, self.action)
        return result


class Or:
    def __init__(self, *args):
        self.rules_or_conditions = args
        self.errors = []

    def clear(self):
        self.errors = []

    def get_error(self, *args):
        return OrMutableException(self.errors)

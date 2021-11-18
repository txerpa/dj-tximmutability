# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta, abstractmethod

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from model_utils import FieldTracker

from tximmutability.rule import MutabilityRule

logger = logging.getLogger('tximmutability')


class BaseMutableModelAction(object):
    """
    Action performed on the instance of an mutable model.
    To implement concrete MutableModelAction it is obligatory to define action name
    and to implement is_allowed method

    To validate action against immutability rules call validate(rules) method
    """

    # output = _('Today is %(month)s %(day)s.') % {'month': m, 'day': d}
    __metaclass__ = ABCMeta

    def __init__(self, model_instance):
        self.model_instance = model_instance

    def error_message(self, rule=None):
        return rule.error_message % {'action': self.action} or _(
            f'This item could not be {self.action}.'
        )

    @property
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def is_allowed(self, rule):
        """
        Check if the action on the concrete item is allowed by the given rule
        :param rule: ImmutabilityRule
        :return: bool
        """
        pass

    def validate(self, mutability_rules):
        """
        :param: MutableModelAction []
        :raise: ValidationError
        """
        for rule in mutability_rules:
            if not self.is_allowed(rule):
                raise ValidationError(self.error_message(rule))


class BaseMutableModelCreate(BaseMutableModelAction):
    action = _('create')

    def is_allowed(self, rule):
        """
        Create is allowed if rule byself allow creation or if model is in mutable state
        """
        return rule.exclude_on_create or rule.is_mutable(self.model_instance)


class BaseMutableModelUpdate(BaseMutableModelAction):
    action = _('update')
    errors = {}

    def __init__(self, model_instance):
        self.errors = {}
        super(BaseMutableModelUpdate, self).__init__(model_instance)

    def validate(self, mutability_rules):
        """
        :param: MutableModelAction []
        :raise: ValidationError
        """
        for rule in mutability_rules:
            self.is_allowed(rule)

        if self.errors:
            raise ValidationError(self.errors)

    def is_allowed(self, rule):
        """
        Update of the instance field for the given rule is allowed if one of the following cases is fulfill:
        - update is allowed by rule
        - rule is defined for the field we want to update
        - field is defined as one of mutable fields in rule
        - Model instance is in mutable state
        :param rule: ImmutabilityRule
        :return: bool
        """

        allowed = True
        if rule.exclude_on_update:
            return True

        db_column_names = [
            self.model_instance._meta.get_field(f).column
            for f in rule.exclude_fields
        ]
        _is_mutable = rule.is_mutable(self.model_instance)
        for field, value in self.model_instance.tracker.changed().items():
            if field in db_column_names:
                # excluded field
                continue

            if field == rule.field_rule:
                # same rule field
                continue

            if not _is_mutable:
                self.errors[field] = self.error_message(rule)
                allowed = False

        return allowed


class BaseMutableModelDelete(BaseMutableModelAction):
    action = _('delete')

    def is_allowed(self, rule):
        """
        Delete of the instance is allowed if rule by self allow delete or if instance is in mutable state
        """
        return rule.exclude_on_delete or rule.is_mutable(self.model_instance)


class AbstractFieldTracker(FieldTracker):
    def finalize_class(self, sender, name='tracker', **kwargs):
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super().finalize_class(sender, **kwargs)


class MutableModel(models.Model):
    """
    Immutable model is a model which has set of immutability rules defined in param mutability_rules.
    By the each rule is defined the case when an instance of the given model is immutable.

    Whenever an action (update, create or delete) is called, it will be validated for the each rule
    in order to check whether there is a rule for which is not allowed to perform action.

    If you want to ignore immutability rules and force execution of the action set param force to True
    """

    mutability_rules = ()
    trackable_fields = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        # Workaround for FieldTracker issue: https://github.com/jazzband/django-model-utils/issues/155
        tracker = AbstractFieldTracker(fields=self.trackable_fields)
        tracker.finalize_class(self.__class__)
        self.check_mutability_rules()
        super().__init__(*args, **kwargs)

    def check_mutability_rules(self):
        model_name = getattr(self.Meta, 'verbose_name', self.__class__.__name__)
        if not isinstance(self.mutability_rules, (tuple, list)):
            raise TypeError(
                _(
                    '%s.mutability_rules attribute must be '
                    'a list.' % model_name
                )
            )
        if any(
            not isinstance(rule, MutabilityRule)
            for rule in self.mutability_rules
        ):
            raise TypeError(
                _(
                    '%s.mutability_rule attribute must be an instance of \"MutabilityRule\".'
                    % model_name
                )
            )

    def save(self, *args, **kwargs):
        tx_force = kwargs.pop("force", False)
        if not tx_force:
            if not self.pk:
                BaseMutableModelCreate(self).validate(self.mutability_rules)
            else:
                BaseMutableModelUpdate(self).validate(self.mutability_rules)
        super(MutableModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete object if there is no restrictions
        To force delete set param force to True
        """
        tx_force = kwargs.pop('force', False)
        if not tx_force:
            BaseMutableModelDelete(self).validate(self.mutability_rules)
        super(MutableModel, self).delete(*args, **kwargs)

    def saved_value(self, field):
        """
        Method to get field value saved at DB.
        """
        raise NotImplementedError(
            "Subclasses of MutableModel must provide a \"saved_value\" method"
        )

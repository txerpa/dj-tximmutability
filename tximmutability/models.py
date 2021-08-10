# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from abc import ABCMeta
from abc import abstractmethod

from django.db import models
from django.utils.translation import gettext as _
from rest_framework.serializers import ValidationError
from tximmutability.rule import MutabilityRule
logger = logging.getLogger('tximmutability')


class BaseImmutableModelAction(object):
    """
    Action performed on the instance of an immutable model.
    To implement concrete ImmutableModelAction it is obligatory to define action name 
    and to implement is_allowed method

    To validate action against immutability rules call validate(rules) method  
    """
    # output = _('Today is %(month)s %(day)s.') % {'month': m, 'day': d}
    __metaclass__ = ABCMeta

    def __init__(self, model_instance):
        self.model_instance = model_instance

    def error_message(self, rule=None):
        if isinstance(rule, MutabilityRule):
            return rule.error_message % {'action': self.action}
        return _('El item no se ha podido %(action).') % {'action': self.action}

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

    def validate(self, immutability_rules):
        """
        :param: ImmutableModelAction []
        :raise: ValidationError 
        """
        for rule in immutability_rules:
            if not self.is_allowed(rule):
                raise ValidationError(self.error_message(rule))


class BaseImmutableModelCreate(BaseImmutableModelAction):
    action = 'crear'

    def is_allowed(self, rule):
        """
        Create is allowed if rule byself allow creation or if model is in mutable state
        """
        return rule.exclude_on_create or rule.is_mutable(self.model_instance)


class BaseImmutableModelUpdate(BaseImmutableModelAction):
    action = 'editar'
    errors = {}

    def __init__(self, model_instance):
        super(BaseImmutableModelUpdate, self).__init__(model_instance)

    def validate(self, immutability_rules):
        """
        :param: ImmutableModelAction []
        :raise: ValidationError
        """
        for rule in immutability_rules:
            self.is_allowed(rule)

        if self.errors:
            import inspect
            stack = inspect.stack()
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

        for field, value in self.model_instance.tracker.changed().items():
            logger.info(_("Field updated"), field, value)

            if field in rule.exclude_fields:
                # excluded field
                continue

            if field == rule.field_name:
                # same rule field
                continue

            # [tup[1] for tup in string.Formatter().parse(my_string) if tup[1] is not None]
            if not rule.is_mutable(self.model_instance):
                self.errors[field] = self.error_message(rule)
                allowed = False

        return allowed


class BaseImmutableModelDelete(BaseImmutableModelAction):
    action = 'borrar'

    def is_allowed(self, rule):
        """
        Delete of the instance is allowed if rule by self allow delete or if instance is in mutable state
        """
        return rule.exclude_on_delete or rule.is_mutable(self.model_instance)


class ImmutableModel(models.Model):
    """
     Immutable model is a model which has set of immutability rules defined in param immutability_rules.
     By the each rule is defined the case when an instance of the given model is immutable.

     Whenever an action (update, create or delete) is called, it will be validated for the each rule
     in order to check whether there is a rule for which is not allowed to perform action.

     If you want to ignore immutability rules and force execution of the action set param force to True
    """
    immutability_rules = ()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ImmutableModel, self).__init__(*args, **kwargs)
        self.check_immutability_rules()

    def check_immutability_rules(self):
        if not isinstance(self.immutability_rules, (tuple, list)):
            raise TypeError(_('immutability_rules attribute in %s must be '
                            'a list' % self.Meta.verbose_name))
        if any(not isinstance(rule, MutabilityRule) for rule in self.immutability_rules):
            raise TypeError(_('%s: immutability rule item has to be ImmutabilityRule type' % self.Meta.verbose_name))

    def save(self, *args, **kwargs):
        tx_force = kwargs.pop("force", False)
        if not tx_force:
            if not self.pk:
                BaseImmutableModelCreate(self).validate(self.immutability_rules)
            else:
                BaseImmutableModelUpdate(self).validate(self.immutability_rules)
        super(ImmutableModel, self).save(*args, **kwargs)

    # def update(self, validated_data, force=False, save_kwargs={}):
    #     """
    #     Set each attribute on the instance, and then save it.
    #     In case of error, accumulate them and after checking all fields
    #     raise an ValidationError with all error messages
    #     :param validated_data: {{*}}
    #     :param force: bool if update need to be forced
    #     :param save_kwargs: kwargs params passed to django save method
    #     :raise: ValidationError
    #     """
    #     errors = {}
    #     for field, value in validated_data.items():
    #         try:
    #             self.update_attribute(field, value, force=force)
    #         except ValidationError as exc:
    #             errors[field] = exc.detail
    #     if errors:
    #         raise ValidationError(errors)
    #     self.save(**save_kwargs)

    # def update_attribute(self, name, value, force=False):
    #     """
    #     Update attribute value only after checking its mutability
    #     To force update set parameter force to True
    #     :param name: attribute name
    #     :param value: new attribute value
    #     """
    #     if not force:
    #         BaseImmutableModelUpdate(self, name).validate(self.immutability_rules)
    #     setattr(self, name, value)

    def delete(self, *args, **kwargs):
        """
        Delete object if there is no restrictions
        To force delete set param force to True
        """
        tx_force = kwargs.pop('force', False)
        if not tx_force:
            BaseImmutableModelDelete(self).validate(self.immutability_rules)
        super(ImmutableModel, self).delete(*args, **kwargs)

    def saved_value(self, field):
        """
        Mehtod to get field value saved at DB.
        """
        raise NotImplementedError('subclasses of ImmutableModel must provide a saved_value() method')

# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from rest_framework.serializers import ValidationError
from tximmutability.rule import ImmutabilityRule
from abc import ABCMeta, abstractmethod, abstractproperty


class BaseImmutableModelAction(object):
    """
    Action performed on the instance of an immutable model.
    To implement concrete ImmutableModelAction it is obligatory to define action name 
    and to implement is_allowed method

    To validate action against immutability rules call validate(rules) method  
    """
    __metaclass__ = ABCMeta

    def __init__(self, model_instance):
        self.model_instance = model_instance

    @abstractmethod
    def name(self):
        pass

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
                message = rule.error_message or f'No se puede {self.name} ítem'
                raise ValidationError(message)


class BaseImmutableModelCreate(BaseImmutableModelAction):
    name = 'crear'

    def is_allowed(self, rule):
        """
        Create is allowed if rule byself allow creation or if model is in mutable state
        """
        return rule.allow_create or rule.is_object_mutable(self.model_instance)


class BaseImmutableModelUpdate(BaseImmutableModelAction):
    name = 'editar'

    def __init__(self, model_instance, field_name):
        super(BaseImmutableModelUpdate, self).__init__(model_instance)
        self.field_name = field_name

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
        return rule.allow_update or rule.field_name == self.field_name or rule.excluded_field(self.field_name) \
            or rule.is_object_mutable(self.model_instance)


class BaseImmutableModelDelete(BaseImmutableModelAction):
    name = 'borrar'

    def is_allowed(self, rule):
        """
        Delete of the instance is allowed if rule by self allow delete or if instance is in mutable state
        """
        return rule.allow_delete or rule.is_object_mutable(self.model_instance)


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
            raise TypeError('immutability_rules attribute in %s must be '
                            'a list' % self.Meta.verbose_name)
        if any(not isinstance(rule, ImmutabilityRule) for rule in self.immutability_rules):
            raise TypeError('%s: immutability rule item has to be ImmutabilityRule type' % self.Meta.verbose_name)

    def save(self, *args, **kwargs):
        if not self.pk:
            BaseImmutableModelCreate(self).validate(self.immutability_rules)
        super(ImmutableModel, self).save(*args, **kwargs)

    def update(self, validated_data, force=False, save_kwargs={}):
        """
        Set each attribute on the instance, and then save it.
        In case of error, accumulate them and after checking all fields
        raise an ValidationError with all error messages
        :param validated_data: {{*}}
        :param force: bool if update need to be forced 
        :param save_kwargs: kwargs params passed to django save method
        :raise: ValidationError 
        """
        errors = {}
        for field, value in validated_data.items():
            try:
                self.update_attribute(field, value, force=force)
            except ValidationError as exc:
                errors[field] = exc.detail
        if errors:
            raise ValidationError(errors)
        self.save(**save_kwargs)

    def update_attribute(self, name, value, force=False):
        """
        Update attribute value only after checking its mutability
        To force update set parameter force to True 
        :param name: attribute name
        :param value: new attribute value
        """
        if not force:
            BaseImmutableModelUpdate(self, name).validate(self.immutability_rules)
        setattr(self, name, value)

    def delete(self, *args, **kwargs):
        """
        Delete object if there is no restrictions
        To force delete set param force to True
        """
        is_forced_action = kwargs.pop('force', False)
        if not is_forced_action:
            BaseImmutableModelDelete(self).validate(self.immutability_rules)
        super(ImmutableModel, self).delete(*args, **kwargs)

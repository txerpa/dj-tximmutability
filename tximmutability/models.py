# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from rest_framework.serializers import ValidationError
from tximmutability.rule import ImmutabilityRule


class ImmutableModel(models.Model):
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
        for rule in self.immutability_rules:
            if not isinstance(rule, ImmutabilityRule):
                raise TypeError('%s: immutability rule item has to be ImmutabilityRule type'
                                % self.Meta.verbose_name)

    def update(self, validated_data, **kwargs):
        """
        Set each attribute on the instance, and then save it.
        In case of error, accumulate them and after checking all fields
        raise an ValidationError with all error messages
        :param validated_data: {{*}}
        :param kwargs: 
        :raise: ValidationError 
        """
        errors = {}
        for field, value in validated_data.items():
            try:
                self.update_attribute(field, value, **kwargs)
            except ValidationError as exc:
                errors[field] = exc.detail
        if errors:
            raise ValidationError(errors)
        self.save()

    def update_attribute(self, name, value, **kwargs):
        """
        Update attribute value only after checking its mutability
        To force update set parameter force to True 
        :param name: attribute name
        :param value: new attribute value
        """
        if not kwargs.get('force', False):
            self.check_mutability(name)
        setattr(self, name, value)

    def delete(self, *args, **kwargs):
        """
        Delete object if there is no restrictions
        To force delete set param force to True
        """
        is_forced_action = kwargs.pop('force', False)
        if not is_forced_action:
            self.check_delete_restriction()
        super(ImmutableModel, self).delete(*args, **kwargs)

    def check_mutability(self, field_name):
        """
        Walk through model immutability rules and if there is a rule 
        for which field is not mutable raise ValidationError with proper message
        :param field_name: str 
        :raise: ValidationError 
        """
        for rule in self.immutability_rules:
            if not rule.is_mutable_field(self, field_name):
                raise ValidationError(rule.format_error_message())

    def check_delete_restriction(self):
        """
        Walk through model immutability rules and if there is a rule 
        for which is not allowed to delete object raise ValidationError with proper message
        :raise: ValidationError 
        """
        for rule in self.immutability_rules:
            if not rule.is_delete_allowed(self):
                raise ValidationError({'error': rule.format_error_message(is_update=False)})

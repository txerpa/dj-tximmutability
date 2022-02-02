# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from django.db import models
from model_utils import FieldTracker

from tximmutability.services import (
    BaseMutableModelCreate,
    BaseMutableModelDelete,
    BaseMutableModelUpdate,
)

logger = logging.getLogger('tximmutability')


class AbstractFieldTracker(FieldTracker):
    def finalize_class(self, sender, name='tracker', **kwargs):
        self.name = name
        self.attname = '_%s' % name
        if not hasattr(sender, name):
            super().finalize_class(sender, **kwargs)


class MutableQuerySet(models.QuerySet):
    def _pre_bulk_update_validate_immutability(self, *args, **kwargs):
        model = self.model
        update_fields = kwargs
        if getattr(model, 'mutability_rules', None):
            if self.exists():
                BaseMutableModelUpdate(
                    queryset=self, update_fields=update_fields.keys()
                ).validate(model.mutability_rules)

    def update(self, *args, **kwargs):
        self._pre_bulk_update_validate_immutability(*args, **kwargs)
        return super().update(*args, **kwargs)


class MutableModel(models.Model):
    """
    Immutable model is a model which has set of immutability rules defined in
    param mutability_rules.
    By the each rule is defined the case when an instance of the given model is
     immutable.

    Whenever an action (update, create or delete) is called, it will be
    validated for the each rule in order to check whether there is a rule for
    which is not allowed to perform action.

    If you want to ignore immutability rules and force execution of the action
    set param force to True
    """

    _mutability_rules = ()
    trackable_fields = None

    objects = MutableQuerySet.as_manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        # Workaround for FieldTracker issue:
        # https://github.com/jazzband/django-model-utils/issues/155
        tracker = AbstractFieldTracker(fields=self.trackable_fields)
        tracker.finalize_class(self.__class__)
        super().__init__(*args, **kwargs)

    @property
    def mutability_rules(self):
        return self._mutability_rules

    def save(self, *args, **kwargs):
        tx_force = kwargs.pop("force", False)
        if not tx_force:
            if not self.pk:
                BaseMutableModelCreate(self).validate(self._mutability_rules)
            else:
                BaseMutableModelUpdate(self).validate(self._mutability_rules)
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

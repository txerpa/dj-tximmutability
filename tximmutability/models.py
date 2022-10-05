# -*- coding: utf-8 -*-

import logging

from django.db import models
from model_utils import FieldTracker

from .services import (
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
    def __init__(self, *args, **kwargs):
        self.force_mutability = kwargs.pop("force_mutability", False)
        super().__init__(*args, **kwargs)

    def _pre_bulk_update_validate_immutability(self, *args, **kwargs):
        model = self.model
        update_fields = kwargs
        if getattr(model, '_mutability_rules', None):
            if self.exists():
                BaseMutableModelUpdate(
                    self, update_fields=update_fields.keys()
                ).validate(model._mutability_rules)

    def update(self, force_mutability=None, *args, **kwargs):
        if not getattr(self, 'force_mutability', force_mutability):
            self._pre_bulk_update_validate_immutability(*args, **kwargs)
        return super().update(*args, **kwargs)

    def bulk_update(self, objs, fields, batch_size=None, force_mutability=None):
        force_mutability_original_value = self.force_mutability
        self.force_mutability = force_mutability or False
        super().bulk_update(objs, fields, batch_size=batch_size)
        self.force_mutability = force_mutability_original_value

    def _clone(self):
        c = super()._clone()
        c.force_mutability = self.force_mutability or False
        return c


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

    def save(self, *args, **kwargs):
        force_mutability = kwargs.pop("force_mutability", False)
        if not force_mutability:
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
        force_mutability = kwargs.pop('force_mutability', False)
        if not force_mutability:
            BaseMutableModelDelete(self).validate(self._mutability_rules)
        super(MutableModel, self).delete(*args, **kwargs)

    def saved_value(self, field):
        """
        Method to get field value saved at DB.
        """
        raise NotImplementedError(
            "Subclasses of MutableModel must provide a \"saved_value\" method"
        )

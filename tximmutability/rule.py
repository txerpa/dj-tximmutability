# coding=utf-8

import logging

from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, RelatedField
from django.utils.translation import gettext as _

logger = logging.getLogger('txmutability')


class MutabilityRule:
    """
    This class serves to define the rule when an model is mutable.
    To define mutability rule it is mandatory to define "field_rule"
    of the model from which depend model mutability.
    To define relation field use '__' as separator in "field_rule"

    Once, "field_rule" is defined, model becomes immutable if the rule is not fulfilled (you can not update
    it or delete it).

    Parameters
    ----------
        field_rule <String>: field mutability effects.
        values <set>: set of values to establish when the model will be mutable.
        exclude_fields <set>: set of fields names to exclude for this rule.
        exclude_on_create <Bool>: To exclude this rule on create set <True>, otherwise <False>. Default True
        exclude_on_update <Bool>: To exclude this rule on update set <True>, otherwise <False>. Default False
        exclude_on_delete <Bool>: To exclude this rule on delete set <True>, otherwise <False>. Default False
        error_message  <String>: Message passed on raise.

    Examples:
        - Only invoice note can be changed if invoice is not in draft state.
        MutabilityRule('state', values=('draft',), exclude_fields=('note',))
        - Entry can not be deleted (but can be updated) if related invoice is validated
        MutabilityRule('invoice__state', values=('draft',), exclude_on_update=True)
        - Invoice line cannot be updated or deleted nor new line can be added if invoice is not in draft or budget state
        MutabilityRule('invoice__state', values=('draft', 'budget'), exclude_on_create=False)
    """

    def __init__(
        self,
        field_rule,
        values=(),
        exclude_fields=(),
        exclude_on_create=True,
        exclude_on_update=False,
        exclude_on_delete=False,
        error_message="",
    ):
        """
        param fields_data: dict {<field_name>: set(<values for each field>)}, like {"name": ('tim', 'tom', 'tam')}
        """
        self.field_rule = field_rule
        self.values = values
        self.exclude_fields = exclude_fields

        self.exclude_on_create = exclude_on_create
        self.exclude_on_update = exclude_on_update
        self.exclude_on_delete = exclude_on_delete

        self.error_message = error_message

    def is_mutable(self, model_instance, field_parts=None):
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
        If there are more related objects (relation is many_to_many or one_to_many)
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
                if not self.is_mutable(related_object, field_parts=rel_parts):
                    return False
            return True
        else:
            return self.is_mutable(value, field_parts=rel_parts)

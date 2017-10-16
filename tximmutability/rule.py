# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.db.models import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, RelatedField


class ImmutabilityRule(object):
    """
    This class serves to define the rule when an model is immutable.
    To define immutability rule it is obligatory to define field name
    of the model from which depend model immutability. To define relation field use '__' as separator

    Once field value is defined model becomes immutable(you can not update it or delete it).
    To allow update/delete of the object set param allow_update/allow_delete to True.
    By default immutable object can be created. To forbid creation set allow_create to False

    To allow object mutability for the specific field's values
    define that values in mutable_states param

    To exclude some fields from the rule and make them mutable define field names in 
    mutable_fields param

    Examples:
        - Only invoice note can be changed if invoice is not in draft state.
        ImmutabilityRule('estado', mutable_states=('draft',), mutable_fields=('note',))
        - Entry can not be deleted (but can be updated) if related invoice is validated 
        ImmutabilityRule('factura__estado', mutable_states=('draft',), allow_update=True)
        - Invoice line cannot be updated or deleted nor new line can be added if invoice is not in draft or budget state
        ImmutabilityRule('factura__estado', mutable_states=('draft', 'budget'), allow_create=False)
    """
    def __init__(self, field_name, mutable_states=(), mutable_fields=(),
                 allow_update=False, allow_delete=False, allow_create=True, error_message=""):
        self.field_name = field_name
        self.mutable_states = mutable_states
        self.mutable_fields = mutable_fields
        self.allow_update = allow_update
        self.allow_delete = allow_delete
        self.allow_create = allow_create
        self.error_message = error_message

    def is_object_mutable(self, model_instance, field_parts=None):
        """
        Check if model obj is in mutable state.
        Model obj is in mutable state if field defined by rule has 
        one of the values defined in mutable_states. If field is relation check 
        if relation is mutable
        :param model_instance: TxerpadBase
        :param field_parts: name of the field or related object field 
        (e.g 'estado' or 'factura__estado') 
        :return: bool
        """
        field_parts = field_parts or self.field_name.split('__')
        opts = model_instance._meta

        # walk relationships
        for field_name in field_parts:
            try:
                rel = opts.get_field(field_name)
            except FieldDoesNotExist:
                return True
            if isinstance(rel, (RelatedField, ForeignObjectRel)):
                # field is forward or reverse relation
                rel_parts = field_parts[field_parts.index(field_name) + 1:]
                if isinstance(rel, ForeignObjectRel):
                    field_name = rel.get_accessor_name()
                field_val = getattr(model_instance, field_name)
                return self.is_relation_mutable(rel, field_val, rel_parts)
            else:
                # field is model attribute
                field_val = getattr(model_instance, field_name, None)
                return field_val in self.mutable_states

    def is_relation_mutable(self, relation, value, rel_parts):
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
            return value in self.mutable_states
        if not value:
            return True
        if relation.many_to_many or relation.one_to_many:
            for related_object in value.all():
                if not self.is_object_mutable(related_object, field_parts=rel_parts):
                    return False
            return True
        else:
            return self.is_object_mutable(value, field_parts=rel_parts)

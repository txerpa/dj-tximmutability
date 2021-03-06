# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from rest_framework.serializers import ValidationError

from tests.testapp.constants import ModelState
from tests.testapp.models import ImmutableModelAllowDelete, BaseImmutableModel, ImmutableModelAllowUpdate, \
    ImmutableReverseRelationModel, ImmutableRelationModel, ModelWithRelation, \
    ImmutableMultiForwardRelModel, ImmutableMultiReverseRelModel, ImmutableMultiMixRelModel


class TestModelImmutability(object):
    """Base class for testing model immutability"""

    @property
    def immutable_model(self):
        raise NotImplementedError()

    @property
    def immutable_object(self):
        raise NotImplementedError()

    @property
    def immutability_depend_object(self):
        raise NotImplementedError()

    def test_cant_update_field_when_model_is_immutable(self):
        self.assertRaises(ValidationError, self.immutable_object.update_attribute, 'name', 'Mutable')

    def test_can_update_field_when_model_is_mutable(self):
        self.immutability_depend_object.state = ModelState.MUTABLE_STATE
        self.immutability_depend_object.save()
        self.immutable_object.update_attribute('name', 'Mutable')
        self.assertEqual(self.immutable_object.name, 'Mutable')

    def test_cant_delete_when_model_is_immutable(self):
        self.assertRaises(ValidationError, self.immutable_object.delete)

    def test_can_delete_when_model_is_mutable(self):
        self.immutability_depend_object.state = ModelState.MUTABLE_STATE
        self.immutability_depend_object.save()
        self.immutable_object.delete()
        self.assertEqual(0, len(self.immutable_model.objects.all()))

    def test_force_delete_when_model_is_immutable(self):
        self.immutable_object.delete(force=True)
        self.assertEqual(0, len(self.immutable_model.objects.all()))

    def test_force_update_when_model_is_immutable(self):
        self.immutable_object.update_attribute('state', ModelState.MUTABLE_STATE, force=True)
        self.assertEqual(self.immutable_object.state, ModelState.MUTABLE_STATE)


class TestBaseModel(TestModelImmutability, TestCase):
    immutable_model = BaseImmutableModel

    @property
    def immutable_object(self):
        return self.base_immutable_object

    @property
    def immutability_depend_object(self):
        return self.base_immutable_object

    def setUp(self):
        self.base_immutable_object = self.immutable_model.objects.create()

    def test_can_update_rule_field_when_model_is_immutable(self):
        self.immutable_object.update_attribute('state', ModelState.MUTABLE_STATE)
        self.assertEqual(self.immutable_object.state, ModelState.MUTABLE_STATE)

    def test_can_update_mutable_fields_when_model_is_immutable(self):
        self.immutable_object.update_attribute('description', 'Test')
        self.assertEqual(self.immutable_object.description, 'Test')

    def test_cant_update_model_when_immutable_field_is_included(self):
        self.assertRaises(ValidationError, self.immutable_object.update, {
            'description': ModelState.MUTABLE_STATE,
            'name': 'Mutable'
        })

    def test_custom_error_message_on_delete(self):
        with self.assertRaisesMessage(ValidationError,
                                      "{u'error': u'No se puede borrar, estado es inmutable'}"):
            self.immutable_object.delete()

    def test_custom_error_message_on_update(self):
        with self.assertRaisesMessage(ValidationError,
                                      "{u'name': [u'No se puede editar, estado es inmutable']}"):
            self.immutable_object.update({'name': 'Mutable'})


class TestRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableRelationModel

    @property
    def immutable_object(self):
        return self.relation_immutable_object

    @property
    def immutability_depend_object(self):
        return self.relation_immutable_object.related_field

    def setUp(self):
        self.relation_immutable_object = self.immutable_model.objects.create(
            related_field=BaseImmutableModel.objects.create()
        )


class TestMultiForwardRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableMultiForwardRelModel

    @property
    def immutable_object(self):
        return self.multi_rel_immutable_object

    @property
    def immutability_depend_object(self):
        return self.multi_rel_immutable_object.related_field.related_field

    def setUp(self):
        self.multi_rel_immutable_object = self.immutable_model.objects.create(
            related_field=ModelWithRelation.objects.create(
                related_field=ImmutableReverseRelationModel.objects.create()
            )
        )


class TestReverseRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableReverseRelationModel

    @property
    def immutable_object(self):
        return self.relation_object.related_field

    @property
    def immutability_depend_object(self):
        return self.relation_object

    def setUp(self):
        self.relation_object = ModelWithRelation.objects.create(
            related_field=self.immutable_model.objects.create()
        )


class TestMultiReverseRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableMultiReverseRelModel

    @property
    def immutable_object(self):
        return self.relation_object.related_field.related_field

    @property
    def immutability_depend_object(self):
        return self.relation_object

    def setUp(self):
        self.relation_object = ModelWithRelation.objects.create(
            related_field=ImmutableReverseRelationModel.objects.create(
                related_field=self.immutable_model.objects.create()
            )
        )


class TestForwardReverseRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableMultiMixRelModel

    @property
    def immutable_object(self):
        return self.forward_reverse_rel_object

    @property
    def immutability_depend_object(self):
        return self.immutable_relation_model

    def setUp(self):
        base_immutable_model = BaseImmutableModel.objects.create()
        self.immutable_relation_model = ImmutableRelationModel.objects.create(
            related_field=base_immutable_model
        )
        self.forward_reverse_rel_object = self.immutable_model.objects.create(
            related_field=base_immutable_model
        )


class TestReverseForwardRelation(TestModelImmutability, TestCase):
    immutable_model = ImmutableMultiMixRelModel

    @property
    def immutable_object(self):
        return self.reverse_forward_rel_object

    @property
    def immutability_depend_object(self):
        return self.end_relation

    def setUp(self):
        self.reverse_forward_rel_object = self.immutable_model.objects.create()
        self.end_relation = ImmutableReverseRelationModel.objects.create()
        ModelWithRelation.objects.create(
            related_field2=self.reverse_forward_rel_object,
            related_field=self.end_relation
        )


class TestModelImmutabilityDeleteAllowed(TestCase):
    def setUp(self):
        self.immutable_object = ImmutableModelAllowDelete.objects.create()

    def test_can_delete(self):
        self.immutable_object.delete()
        self.assertEqual(0, len(ImmutableModelAllowDelete.objects.all()))


class TestModelImmutabilityUpdateAllowed(TestCase):
    def setUp(self):
        self.immutable_object = ImmutableModelAllowUpdate.objects.create()

    def test_can_update(self):
        self.immutable_object.update_attribute('name', 'Mutable')
        self.assertEqual(self.immutable_object.name, 'Mutable')



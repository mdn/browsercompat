'''
Tests for drf_cached_reads/models.py
'''
from django.contrib.auth.models import User
from django.test import TestCase

from drf_cached_reads.models import CachedModel, CachedQueryset

from .cache import UserCache


class TestCachedModel(TestCase):
    def test_has_data(self):
        cm = CachedModel(User, {'username': 'frank'})
        self.assertEqual('frank', cm.username)

    def test_does_not_have_data(self):
        cm = CachedModel(User, {'username': 'frank'})
        self.assertRaises(AttributeError, getattr, cm, 'email')


class TestCachedQueryset(TestCase):
    def setUp(self):
        self.cache = UserCache()

    def test_get_existing_instance(self):
        user = User.objects.create(username='frank')
        cq = CachedQueryset(self.cache, User.objects.all())
        cached_user = cq.get(pk=user.pk)
        self.assertEqual('frank', cached_user.username)

    def test_get_nonexisting_instance(self):
        self.assertFalse(User.objects.filter(pk=666).exists())
        cq = CachedQueryset(self.cache, User.objects.all())
        self.assertRaises(User.DoesNotExist, cq.get, pk=666)

    def test_none(self):
        cq = CachedQueryset(self.cache, User.objects.all())
        cq_none = cq.none()
        self.assertEqual([], cq_none.pks)

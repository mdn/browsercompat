'''
Tests for drf_cached_reads/cache.py

These tests are not complete, and will have to be expanded if drf_cached_reads
is split from the webplatformcompat project.  However, this will require a set
of test views and models, so it is being deferred until then.
'''

from datetime import datetime, date
import mock

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.utils import override_settings
from pytz import UTC

from drf_cached_reads.cache import (
    BaseCache, CachedModel, CachedQueryset, PkOnlyModel, PkOnlyValuesList)


class UserCache(BaseCache):
    '''Test cache that cached User instances'''

    def user_default_serializer(self, obj):
        if not obj:
            return None
        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
        ))

    def user_default_loader(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def user_default_invalidator(self, obj):
        return ['drfc_user_count']

    group_default_serializer = None

    def group_default_loader(self, pk):
        return Group.objects.get(pk=pk)

    def group_default_invalidator(self, obj):
        user_pks = User.objects.values_list('pk', flat=True)
        return [('User', pk, False) for pk in user_pks]

    bar_default_serializer = None
    bar_default_loader = None
    bar_default_invalidator = None


class SharedCacheTests(object):

    def test_get_instances_no_specs(self):
        instances = self.cache.get_instances([])
        self.assertEqual({}, instances)

    def test_get_instances_cache_miss_no_obj(self):
        date_joined = datetime(2014, 9, 22, 9, 11, tzinfo=UTC)
        user = User.objects.create(
            username='the_user', date_joined=date_joined)
        instances = self.cache.get_instances([('User', user.pk, None)])
        expected = {
            ('User', user.pk): (
                {
                    'id': user.pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                },
                'drfc_default_User_1',
                user,
            ),
        }
        self.assertEqual(expected, instances)

    def test_get_instances_cache_miss_with_obj(self):
        date_joined = datetime(2014, 9, 22, 9, 11, tzinfo=UTC)
        user = User.objects.create(
            username='the_user', date_joined=date_joined)
        instances = self.cache.get_instances([('User', user.pk, user)])
        expected = {
            ('User', user.pk): (
                {
                    'id': user.pk,
                    'username': 'the_user',
                    'date_joined': date_joined,
                },
                'drfc_default_User_1',
                user,
            ),
        }
        self.assertEqual(expected, instances)

    def test_get_instances_invalid_pk(self):
        self.assertFalse(User.objects.filter(pk=666).exists())
        instances = self.cache.get_instances([('User', 666, None)])
        self.assertEqual({}, instances)

    def test_update_instance_invalid_model(self):
        self.assertRaises(AttributeError, self.cache.update_instance, 'Foo', 1)

    def test_update_instance_unhandled_model(self):
        instances = self.cache.update_instance('Bar', 666)
        self.assertEqual([], instances)


@override_settings(USE_INSTANCE_CACHE=True)
class TestCache(SharedCacheTests, TestCase):
    def setUp(self):
        self.cache = UserCache()
        self.cache.cache.clear()
        self.mock_delete = mock.Mock()
        self.cache.cache.delete = self.mock_delete

    def test_update_instance_invalidator_only(self):
        user = User.objects.create(username='A user')
        group = Group.objects.create()
        group.user_set.add(user)
        invalid = self.cache.update_instance('Group', group.pk)
        self.assertEqual([('User', user.pk, 'default')], invalid)

    def test_update_instance_deleted_model(self):
        self.assertFalse(User.objects.filter(pk=666).exists())
        invalid = self.cache.update_instance('User', 666)
        self.assertEqual([], invalid)
        self.mock_delete.assertCalledOnce('foo')

    def test_update_instance_cache_string(self):
        user = User.objects.create(username='username')
        invalid = self.cache.update_instance('User', user.pk)
        self.assertEqual([], invalid)
        self.mock_delete.assertCalledOnce('drfc_user_count')


@override_settings(USE_INSTANCE_CACHE=False)
class TestCacheDisabled(SharedCacheTests, TestCase):
    def setUp(self):
        self.cache = UserCache()


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


class TestFieldConverters(TestCase):
    def setUp(self):
        self.cache = BaseCache()

    def test_date(self):
        the_date = date(2014, 9, 22)
        converted = self.cache.field_date_to_json(the_date)
        self.assertEqual(converted, [2014, 9, 22])
        out = self.cache.field_date_from_json(converted)
        self.assertEqual(out, the_date)

    def test_datetime_with_ms(self):
        dt = datetime(2014, 9, 22, 8, 52, 0, 123456, UTC)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, '1411375920.123456')
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, dt)

    def test_datetime_without_ms(self):
        dt = datetime(2014, 9, 22, 8, 52, 0, 0, UTC)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, 1411375920)
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, dt)

    def test_datetime_without_timezone(self):
        dt = datetime(2014, 9, 22, 8, 52, 0, 123456)
        converted = self.cache.field_datetime_to_json(dt)
        self.assertEqual(converted, '1411375920.123456')
        out = self.cache.field_datetime_from_json(converted)
        self.assertEqual(out, datetime(2014, 9, 22, 8, 52, 0, 123456, UTC))

    def test_pklist(self):
        converted = self.cache.field_pklist_to_json(User, (1, 2, 3))
        expected = {
            'app': 'auth',
            'model': 'user',
            'pks': [1, 2, 3],
        }
        self.assertEqual(converted, expected)
        out = self.cache.field_pklist_from_json(converted)
        self.assertIsInstance(out, PkOnlyValuesList)
        self.assertEqual(User, out.model)
        self.assertEqual([1, 2, 3], out.pks)

    def test_pk(self):
        converted = self.cache.field_pk_to_json(User, 1)
        expected = {
            'app': 'auth',
            'model': 'user',
            'pk': 1,
        }
        self.assertEqual(converted, expected)
        out = self.cache.field_pk_from_json(converted)
        self.assertIsInstance(out, PkOnlyModel)
        self.assertEqual(User, out.model)
        self.assertEqual(1, out.pk)

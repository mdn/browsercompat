"""Cache implementation for tests

This assumes that the user isn't replacing the user model.
"""

from django.contrib.auth.models import User, Group

from drf_cached_reads.cache import BaseCache


class UserCache(BaseCache):
    """Test cache that cached User instances"""

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

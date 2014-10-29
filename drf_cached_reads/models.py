# -*- coding: utf-8 -*-
"""Cache model-like classes

These classes are look-alike replacements for django.db.model.Model and
Queryset.  The full interface is not implemented, only enough to use then
in common Django REST Framework use cases.
"""


class PkOnlyModel(object):
    """Pretend to be a Django model with only the pk set"""

    def __init__(self, cache, model, pk):
        self.cache = cache
        self.model = model
        self.pk = pk


class PkOnlyValuesList(object):
    """Pretend to be a Django queryset / values list"""

    def __init__(self, cache, model, pks):
        self.cache = cache
        self.model = model
        self.pks = pks

    def __iter__(self):
        for pk in self.pks:
            yield PkOnlyModel(self.cache, self.model, pk)

    def __getitem__(self, index):
        return self.pks[index]

    def all(self):
        return self

    def values_list(self, *args, **kwargs):
        """Return a list of values.

        The only valid call is values_list('pk', flat=True)
        """
        flat = kwargs.pop('flat', False)
        assert flat is True
        assert len(args) == 1
        assert args[0] == self.model._meta.pk.name
        return self


class CachedModel(object):
    """Pretend to be a Django model, backed by the cached data"""
    def __init__(self, model, data):
        self._model = model
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        else:
            raise AttributeError(
                "%r object has no attribute %r" %
                (self.__class__, name))


class CachedQueryset(object):
    """Pretend to be a Django queryset

    Used like a queryset until loaded from cache
    """
    def __init__(self, cache, queryset, primary_keys=None):
        self.cache = cache
        assert queryset is not None
        self.queryset = queryset
        self.model = queryset.model
        self.filter_kwargs = {}
        self._primary_keys = primary_keys

    @property
    def pks(self):
        if self._primary_keys is None:
            self._primary_keys = list(
                self.queryset.values_list('pk', flat=True))
        return self._primary_keys

    def __iter__(self):
        model_name = self.model.__name__
        object_specs = [(model_name, pk, None) for pk in self.pks]
        instances = self.cache.get_instances(object_specs)
        for pk in self.pks:
            model_data = instances.get((model_name, pk), {})[0]
            yield CachedModel(self.model, model_data)

    def all(self):
        return self

    def none(self):
        return CachedQueryset(self.cache, self.queryset.none(), [])

    def count(self):
        if self._primary_keys is None:
            return self.queryset.count()
        else:
            return len(self.pks)

    def filter(self, **kwargs):
        assert not self._primary_keys
        self.queryset = self.queryset.filter(**kwargs)
        return self

    def get(self, *args, **kwargs):
        assert not args
        assert list(kwargs.keys()) == ['pk']
        pk = kwargs['pk']
        model_name = self.model.__name__
        object_spec = (model_name, pk, None)
        instances = self.cache.get_instances((object_spec,))
        try:
            model_data = instances[(model_name, pk)][0]
        except KeyError:
            raise self.model.DoesNotExist(
                "No match for %r with args %r, kwargs %r" %
                (self.model, args, kwargs))
        else:
            return CachedModel(self.model, model_data)

    def __getitem__(self, key):
        if self._primary_keys is None:
            pks = self.queryset.values_list('pk', flat=True)[key]
        else:
            pks = self.pks[key]
        return CachedQueryset(self.cache, self.queryset, pks)

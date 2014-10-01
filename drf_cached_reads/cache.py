'''Cache classes'''

from calendar import timegm
from datetime import date, datetime
from pytz import utc
import json

from django.db.models.loading import get_model


class PkOnlyModel(object):
    '''Pretend to be a Django model with only the pk set'''

    def __init__(self, cache, model, pk):
        self.cache = cache
        self.model = model
        self.pk = pk


class PkOnlyValuesList(object):
    '''Pretend to be a Django queryset / values list'''

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
        '''Only valid call is values_list('pk', flat=True)'''
        flat = kwargs.pop('flat', False)
        assert flat is True
        assert len(args) == 1
        assert args[0] == self.model._meta.pk.name
        return self


class CachedModel(object):
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
    '''Pretend to be a Django queryset

    Used like a queryset until loaded from cache
    '''
    def __init__(self, cache, queryset, primary_keys=None):
        self.cache = cache
        assert queryset is not None
        self.queryset = queryset
        self.model = queryset.model
        self.filter_kwargs = {}
        self._primary_keys = primary_keys

    @property
    def pks(self):
        if not self._primary_keys:
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


class BaseCache(object):
    '''Base instance cache

    To make the cache useful, create a derived class with methods for
    your Django models.  See drf_cached_reads/tests/test_user_example.py for an
    example.
    '''

    default_version = 'default'
    versions = ['default']

    def __init__(self):
        self._cache = None
        assert self.default_version in self.versions

    @property
    def cache(self):
        if not self._cache:
            # Delay import of cache so that Django Debug Toolbar sees requests
            from django.core.cache import cache
            self._cache = cache
        return self._cache

    def key_for(self, version, model_name, obj_pk):
        '''Get the cache key for the cached representation'''
        return 'drfc_{0}_{1}_{2}'.format(version, model_name, obj_pk)

    def model_function(self, model_name, version, func_name):
        '''Return the model function'''
        assert func_name in ('serializer', 'loader', 'invalidator')
        name = "%s_%s_%s" % (model_name.lower(), version, func_name)
        return getattr(self, name)

    def field_function(self, type_code, func_name):
        '''Return the field function'''
        assert func_name in ('to_json', 'from_json')
        name = "field_%s_%s" % (type_code.lower(), func_name)
        return getattr(self, name)

    def field_to_json(self, type_code, key, *args, **kwargs):
        assert ':' not in key
        to_json = self.field_function(type_code, 'to_json')
        key_and_type = "%s:%s" % (key, type_code)
        json_value = to_json(*args, **kwargs)
        return key_and_type, json_value

    def field_from_json(self, key_and_type, json_value):
        assert ':' in key_and_type
        key, type_code = key_and_type.split(':', 1)
        from_json = self.field_function(type_code, 'from_json')
        value = from_json(json_value)
        return key, value

    def get_instances(self, object_specs, version=None):
        '''Get the cached native representation for one or more objects

        Keyword arguments:
        object_specs - A sequence of triples (model name, pk, obj):
        - model name - the name of the model
        - pk - the primary key of the instance
        - obj - the instance, or None to load it
        version - The cache version to use, or None for default

        To get the 'new object' representation, set pk and obj to None

        Return is a dictionary:
        key - (model name, pk)
        value - (native representation, pk, object or None)
        '''
        ret = dict()
        spec_keys = set()
        cache_keys = []
        version = version or self.default_version

        # Construct all the cache keys to fetch
        for model_name, obj_pk, obj in object_specs:
            assert model_name
            assert obj_pk

            # Get cache keys to fetch
            obj_key = self.key_for(version, model_name, obj_pk)
            spec_keys.add((model_name, obj_pk, obj, obj_key))
            cache_keys.append(obj_key)

        # Fetch the cache keys
        if cache_keys:
            cache_vals = self.cache.get_many(cache_keys)
        else:
            cache_vals = {}

        # Use cached representations, or recreate
        cache_to_set = {}
        for model_name, obj_pk, obj, obj_key in spec_keys:

            # Load cached objects
            obj_val = cache_vals.get(obj_key)
            obj_native = json.loads(obj_val) if obj_val else None

            # Invalid or not set - load from database
            if not obj_native:
                if not obj:
                    loader = self.model_function(model_name, version, 'loader')
                    obj = loader(obj_pk)
                serializer = self.model_function(
                    model_name, version, 'serializer')
                obj_native = serializer(obj) or {}
                if obj_native:
                    cache_to_set[obj_key] = json.dumps(obj_native)

            # Get fields to convert
            keys = [key for key in obj_native.keys() if ':' in key]
            for key in keys:
                json_value = obj_native.pop(key)
                name, value = self.field_from_json(key, json_value)
                assert name not in obj_native
                obj_native[name] = value

            if obj_native:
                ret[(model_name, obj_pk)] = (obj_native, obj_key, obj)

        # Save any new cached representations
        if cache_to_set:
            self.cache.set_many(cache_to_set)

        return ret

    def update_instance(self, model_name, pk, instance=None, version=None):
        '''Create or update a cached instance

        Keyword arguments are:
        model_name - The name of the model
        pk - The primary key of the instance
        instance - The Django model instance, or None to load it
        versions - Version to update, or None for all

        Return is a list of tuples (model name, pk, immediate) that also needs
        to be updated.
        '''
        versions = [version] if version else self.versions
        invalid = []
        for version in versions:
            serializer = self.model_function(model_name, version, 'serializer')
            loader = self.model_function(model_name, version, 'loader')
            invalidator = self.model_function(
                model_name, version, 'invalidator')
            if serializer is None and loader is None and invalidator is None:
                continue

            # Try to load the instance
            if not instance:
                instance = loader(pk)

            if serializer:
                # Get current value, if in cache
                key = self.key_for(version, model_name, pk)
                current_raw = self.cache.get(key)
                current = json.loads(current_raw) if current_raw else None

                # Get new value
                new = serializer(instance)
                deleted = not instance

                # If cache is invalid, update cache
                invalidate = (current != new) or deleted
                if invalidate:
                    if deleted:
                        self.cache.delete(key)
                    else:
                        self.cache.set(key, json.dumps(new))
            else:
                invalidate = True

            # Invalidate upstream caches
            if instance and invalidate:
                for upstream in invalidator(instance):
                    if isinstance(upstream, str):
                        self.cache.delete(upstream)
                    else:
                        m, i, immediate = upstream
                        if immediate:
                            invalidate_key = self.key_for(version, m, i)
                            self.cache.delete(invalidate_key)
                        invalid.append((m, i, version))
        return invalid

    #
    # Built-in Field converters
    #

    def field_date_from_json(self, date_triple):
        '''Convert a date triple to the date'''
        return date(*date_triple) if date_triple else None

    def field_date_to_json(self, day):
        '''Convert a date to a date triple'''
        return [day.year, day.month, day.day] if day else None

    def field_datetime_from_json(self, json_val):
        '''Convert a UTC timestamp to a UTC datetime'''
        return datetime.fromtimestamp(float(json_val), utc)

    def field_datetime_to_json(self, dt):
        '''Convert a datetime to a UTC timestamp w/ microsecond resolution

        datetimes w/o timezone will be assumed to be in UTC
        '''
        ts = timegm(dt.utctimetuple())
        if dt.microsecond:
            return "{0:03f}".format(ts + dt.microsecond / 1000000.0)
        else:
            return ts

    def field_pklist_from_json(self, data):
        '''Load a PkOnlyValuesList from a JSON dict

        This uses the same format as cached_queryset_from_json
        '''
        model = get_model(data['app'], data['model'])
        return PkOnlyValuesList(self, model, data['pks'])

    def field_pklist_to_json(self, model, pks):
        '''Convert a list of primary keys to a JSON dict

        This uses the same format as cached_queryset_to_json
        '''
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        return {
            'app': app_label,
            'model': model_name,
            'pks': list(pks),
        }

    def field_pk_from_json(self, data):
        '''Load a PkOnlyModel from a JSON dict'''
        model = get_model(data['app'], data['model'])
        return PkOnlyModel(self, model, data['pk'])

    def field_pk_to_json(self, model, pk):
        '''Convert a primary key to a JSON dict'''
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        return {
            'app': app_label,
            'model': model_name,
            'pk': pk,
        }

"""Cache functions"""

from django.contrib.auth.models import User

from drf_cached_instances.cache import BaseCache
from .history import Changeset
from .models import (
    Browser, Feature, Maturity, Section, Specification, Support, Version)


class Cache(BaseCache):
    """Instance Cache for webplatformcompat"""
    versions = ('v1',)
    default_version = 'v1'

    def browser_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        versions_pks = getattr(obj, '_version_pks', None)
        if versions_pks is None:
            versions_pks = list(
                obj.versions.values_list('pk', flat=True))

        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('name', obj.name),
            ('note', obj.note),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
            self.field_to_json(
                'PKList', 'versions', model=Version, pks=versions_pks),
        ))

    def browser_v1_loader(self, pk):
        queryset = Browser.objects.all()
        try:
            obj = queryset.get(pk=pk)
        except Browser.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            obj._version_pks = list(
                obj.versions.values_list('pk', flat=True))
            return obj

    def browser_v1_invalidator(self, obj):
        return []

    def changeset_v1_serializer(self, obj):
        if not obj:
            return None

        hbrowser_pks = getattr(obj, '_historical_browsers_pks', None)
        if hbrowser_pks is None:
            hbrowser_pks = list(obj.historical_browsers.values_list(
                'history_id', flat=True))

        hversion_pks = getattr(obj, '_historical_versions_pks', None)
        if hversion_pks is None:
            hversion_pks = list(obj.historical_versions.values_list(
                'history_id', flat=True))

        hfeature_pks = getattr(obj, '_historical_features_pks', None)
        if hfeature_pks is None:
            hfeature_pks = list(obj.historical_features.values_list(
                'history_id', flat=True))

        hspecification_pks = getattr(
            obj, '_historical_specifications_pks', None)
        if hspecification_pks is None:
            hspecification_pks = list(
                obj.historical_specifications.values_list(
                    'history_id', flat=True))

        hsupport_pks = getattr(obj, '_historical_supports_pks', None)
        if hsupport_pks is None:
            hsupport_pks = list(obj.historical_supports.values_list(
                'history_id', flat=True))

        hmaturity_pks = getattr(obj, '_historical_maturities_pks', None)
        if hmaturity_pks is None:
            hmaturity_pks = list(obj.historical_maturities.values_list(
                'history_id', flat=True))

        hsection_pks = getattr(obj, '_historical_sections_pks', None)
        if hsection_pks is None:
            hsection_pks = list(
                obj.historical_sections.values_list('history_id', flat=True))

        return dict((
            ('id', obj.id),
            self.field_to_json('DateTime', 'created', obj.created),
            self.field_to_json('DateTime', 'modified', obj.modified),
            ('closed', obj.closed),
            ('target_resource_type', obj.target_resource_type),
            ('target_resource_id', obj.target_resource_id),
            self.field_to_json('PK', 'user', model=User, pk=obj.user_id),
            self.field_to_json(
                'PKList', 'historical_browsers', model=Browser.history.model,
                pks=hbrowser_pks),
            self.field_to_json(
                'PKList', 'historical_features', model=Feature.history.model,
                pks=hfeature_pks),
            self.field_to_json(
                'PKList', 'historical_maturities',
                model=Maturity.history.model, pks=hmaturity_pks),
            self.field_to_json(
                'PKList', 'historical_sections', model=Section.history.model,
                pks=hsection_pks),
            self.field_to_json(
                'PKList', 'historical_specifications',
                model=Specification.history.model,
                pks=hspecification_pks),
            self.field_to_json(
                'PKList', 'historical_supports', model=Support.history.model,
                pks=hsupport_pks),
            self.field_to_json(
                'PKList', 'historical_versions', model=Version.history.model,
                pks=hversion_pks),
        ))

    def changeset_v1_loader(self, pk):
        queryset = Changeset.objects
        try:
            obj = queryset.get(pk=pk)
        except Changeset.DoesNotExist:
            return None
        else:
            obj._historical_browsers_pks = list(
                obj.historical_browsers.values_list('history_id', flat=True))
            obj._historical_versions_pks = list(
                obj.historical_versions.values_list('history_id', flat=True))
            obj._historical_features_pks = list(
                obj.historical_features.values_list('history_id', flat=True))
            obj._historical_specifications_pks = list(
                obj.historical_specifications.values_list(
                    'history_id', flat=True))
            obj._historical_supports_pks = list(
                obj.historical_supports.values_list('history_id', flat=True))
            obj._historical_maturities_pks = list(
                obj.historical_maturities.values_list(
                    'history_id', flat=True))
            obj._historical_sections_pks = list(
                obj.historical_sections.values_list('history_id', flat=True))
            return obj

    def changeset_v1_invalidator(self, obj):
        return []

    def feature_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        children_pks = getattr(obj, '_children_pks', None)
        if children_pks is None:
            children_pks = list(obj.children.values_list('pk', flat=True))

        support_pks = getattr(obj, '_support_pks', None)
        if support_pks is None:
            support_pks = list(obj.supports.values_list('pk', flat=True))

        section_pks = getattr(obj, '_section_pks', None)
        if section_pks is None:
            section_pks = list(obj.sections.values_list('pk', flat=True))

        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('mdn_path', obj.mdn_path),
            ('experimental', obj.experimental),
            ('standardized', obj.standardized),
            ('stable', obj.stable),
            ('obsolete', obj.obsolete),
            ('name', obj.name),
            self.field_to_json(
                'PKList', 'sections', model=Section, pks=section_pks),
            self.field_to_json(
                'PKList', 'supports', model=Support, pks=support_pks),
            self.field_to_json(
                'PK', 'parent', model=Feature, pk=obj.parent_id),
            self.field_to_json(
                'PKList', 'children', model=Feature, pks=children_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def feature_v1_loader(self, pk):
        queryset = Feature.objects
        try:
            obj = queryset.get(pk=pk)
        except Feature.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            obj._children_pks = list(obj.children.values_list('pk', flat=True))
            obj._support_pks = list(obj.supports.values_list('pk', flat=True))
            obj._section_pks = list(obj.sections.values_list('pk', flat=True))
            return obj

    def feature_v1_invalidator(self, obj):
        pks = []
        if obj.parent_id:
            pks.append(obj.parent_id)
        else:
            pks += list(obj.get_siblings().values_list('pk', flat=True))
        children_pks = getattr(
            obj, '_children_pks',
            list(obj.children.values_list('pk', flat=True)))
        pks += children_pks
        return [('Feature', pk, False) for pk in pks]

    def maturity_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        specification_pks = getattr(obj, '_specification_pks', None)
        if specification_pks is None:
            specification_pks = list(
                obj.specifications.values_list('pk', flat=True))

        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('name', obj.name),
            self.field_to_json(
                'PKList', 'specifications', model=Specification,
                pks=specification_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def maturity_v1_loader(self, pk):
        queryset = Maturity.objects
        try:
            obj = queryset.get(pk=pk)
        except Maturity.DoesNotExist:
            return None
        else:
            obj._specification_pks = list(
                obj.specifications.values_list('pk', flat=True))
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            return obj

    def maturity_v1_invalidator(self, obj):
        return []

    def section_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        feature_pks = getattr(obj, '_feature_pks', None)
        if feature_pks is None:
            feature_pks = list(
                obj.features.all().values_list('pk', flat=True))

        return dict((
            ('id', obj.pk),
            ('number', obj.number),
            ('name', obj.name),
            ('subpath', obj.subpath),
            ('note', obj.note),
            self.field_to_json(
                'PK', 'specification', model=Specification,
                pk=obj.specification_id),
            self.field_to_json(
                'PKList', 'features', model=Feature, pks=feature_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def section_v1_loader(self, pk):
        queryset = Section.objects
        try:
            obj = queryset.get(pk=pk)
        except Section.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            obj._feature_pks = list(
                obj.features.values_list('pk', flat=True))
            return obj

    def section_v1_invalidator(self, obj):
        return [('Specification', obj.specification_id, False)]

    def specification_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        section_pks = getattr(obj, '_section_pks', None)
        if section_pks is None:
            section_pks = list(
                obj.sections.all().values_list('pk', flat=True))

        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('mdn_key', obj.mdn_key),
            ('name', obj.name),
            ('uri', obj.uri),
            self.field_to_json(
                'PKList', 'sections', model=Section, pks=section_pks),
            self.field_to_json(
                'PK', 'maturity', model=Maturity, pk=obj.maturity_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def specification_v1_loader(self, pk):
        queryset = Specification.objects
        try:
            obj = queryset.get(pk=pk)
        except Specification.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            obj._section_pks = list(
                obj.sections.values_list('pk', flat=True))
            return obj

    def specification_v1_invalidator(self, obj):
        return [('Maturity', obj.maturity_id, False)]

    def support_v1_serializer(self, obj):
        if not obj:
            return None

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        return dict((
            ('id', obj.pk),
            ('support', obj.support),
            ('prefix', obj.prefix),
            ('prefix_mandatory', obj.prefix_mandatory),
            ('alternate_name', obj.alternate_name),
            ('alternate_mandatory', obj.alternate_mandatory),
            ('requires_config', obj.requires_config),
            ('default_config', obj.default_config),
            ('protected', obj.protected),
            ('note', obj.note),
            ('footnote', obj.footnote),
            self.field_to_json(
                'PK', 'version', model=Version, pk=obj.version_id),
            self.field_to_json(
                'PK', 'feature', model=Feature, pk=obj.feature_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def support_v1_loader(self, pk):
        queryset = Support.objects
        try:
            obj = queryset.get(pk=pk)
        except Support.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            return obj

    def support_v1_invalidator(self, obj):
        return [
            ("Version", obj.version_id, True),
            ("Feature", obj.feature_id, True),
        ]

    def version_v1_serializer(self, obj):
        if not obj:
            return None

        support_pks = getattr(obj, '_support_pks', None)
        if support_pks is None:
            support_pks = list(obj.supports.values_list('pk', flat=True))

        history_pks = getattr(obj, '_history_pks', None)
        if history_pks is None:
            history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

        return dict((
            ('id', obj.pk),
            ('version', obj.version),
            self.field_to_json('Date', 'release_day', obj.release_day),
            self.field_to_json('Date', 'retirement_day', obj.retirement_day),
            ('status', obj.status),
            ('release_notes_uri', obj.release_notes_uri),
            ('note', obj.note),
            ('_order', obj._order),
            self.field_to_json(
                'PK', 'browser', model=Browser, pk=obj.browser_id),
            self.field_to_json(
                'PKList', 'supports', model=Support, pks=support_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def version_v1_loader(self, pk):
        queryset = Version.objects
        try:
            obj = queryset.select_related('supports__pk').get(pk=pk)
        except Version.DoesNotExist:
            return None
        else:
            obj._support_pks = list(obj.supports.values_list('pk', flat=True))
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            return obj

    def version_v1_invalidator(self, obj):
        return [
            ("Browser", obj.browser_id, True)]

    def user_v1_serializer(self, obj):
        if not obj or not obj.is_active:
            return None
        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
        ))

    def user_v1_loader(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def user_v1_invalidator(self, obj):
        return []

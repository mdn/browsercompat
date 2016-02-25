"""Cache functions."""

from django.conf import settings
from django.contrib.auth.models import User

from drf_cached_instances.cache import BaseCache
from .history import Changeset
from .models import (
    Browser, Feature, Maturity, Reference, Section, Specification, Support,
    Version)


class Cache(BaseCache):
    """Instance Cache for API resources."""

    versions = ('v1',)
    default_version = 'v1'

    def browser_v1_serializer(self, obj):
        if not obj:
            return None
        self.browser_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('name', obj.name),
            ('note', obj.note),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
            self.field_to_json(
                'PKList', 'versions', model=Version, pks=obj._version_pks),
        ))

    def browser_v1_loader(self, pk):
        queryset = Browser.objects.all()
        try:
            obj = queryset.get(pk=pk)
        except Browser.DoesNotExist:
            return None
        else:
            self.browser_v1_add_related_pks(obj)
            return obj

    def browser_v1_add_related_pks(self, obj):
        """Add related primary keys to a Browser instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
        if not hasattr(obj, '_version_pks'):
            obj._version_pks = list(
                obj.versions.values_list('pk', flat=True))

    def browser_v1_invalidator(self, obj):
        return []

    def changeset_v1_serializer(self, obj):
        if not obj:
            return None
        self.changeset_v1_add_related_pks(obj)
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
                pks=obj._historical_browsers_pks),
            self.field_to_json(
                'PKList', 'historical_features', model=Feature.history.model,
                pks=obj._historical_features_pks),
            self.field_to_json(
                'PKList', 'historical_maturities',
                model=Maturity.history.model,
                pks=obj._historical_maturities_pks),
            self.field_to_json(
                'PKList', 'historical_references',
                model=Reference.history.model,
                pks=obj._historical_references_pks),
            self.field_to_json(
                'PKList', 'historical_sections', model=Section.history.model,
                pks=obj._historical_sections_pks),
            self.field_to_json(
                'PKList', 'historical_specifications',
                model=Specification.history.model,
                pks=obj._historical_specifications_pks),
            self.field_to_json(
                'PKList', 'historical_supports', model=Support.history.model,
                pks=obj._historical_supports_pks),
            self.field_to_json(
                'PKList', 'historical_versions', model=Version.history.model,
                pks=obj._historical_versions_pks),
        ))

    def changeset_v1_loader(self, pk):
        queryset = Changeset.objects
        try:
            obj = queryset.get(pk=pk)
        except Changeset.DoesNotExist:
            return None
        else:
            self.changeset_v1_add_related_pks(obj)
            return obj

    def changeset_v1_add_related_pks(self, obj):
        """Add related primary keys to a Changeset instance."""
        if not hasattr(obj, '_historical_browsers_pks'):
            obj._historical_browsers_pks = list(
                obj.historical_browsers.values_list('history_id', flat=True))
        if not hasattr(obj, '_historical_versions_pks'):
            obj._historical_versions_pks = list(
                obj.historical_versions.values_list('history_id', flat=True))
        if not hasattr(obj, '_historical_features_pks'):
            obj._historical_features_pks = list(
                obj.historical_features.values_list('history_id', flat=True))
        if not hasattr(obj, '_historical_specifications_pks'):
            obj._historical_specifications_pks = list(
                obj.historical_specifications.values_list(
                    'history_id', flat=True))
        if not hasattr(obj, '_historical_supports_pks'):
            obj._historical_supports_pks = list(
                obj.historical_supports.values_list('history_id', flat=True))
        if not hasattr(obj, '_historical_maturities_pks'):
            obj._historical_maturities_pks = list(
                obj.historical_maturities.values_list(
                    'history_id', flat=True))
        if not hasattr(obj, '_historical_sections_pks'):
            obj._historical_sections_pks = list(
                obj.historical_sections.values_list('history_id', flat=True))
        if not hasattr(obj, '_historical_references_pks'):
            obj._historical_references_pks = list(
                obj.historical_references.values_list('history_id', flat=True))

    def changeset_v1_invalidator(self, obj):
        return []

    def feature_v1_serializer(self, obj):
        if not obj:
            return None
        self.feature_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('mdn_uri', obj.mdn_uri),
            ('experimental', obj.experimental),
            ('standardized', obj.standardized),
            ('stable', obj.stable),
            ('obsolete', obj.obsolete),
            ('name', obj.name),
            ('descendant_count', obj.descendant_count),
            self.field_to_json(
                'PKList', 'references', model=Reference,
                pks=obj._reference_pks),
            self.field_to_json(
                'PKList', 'supports', model=Support, pks=obj._support_pks),
            self.field_to_json(
                'PK', 'parent', model=Feature, pk=obj.parent_id),
            self.field_to_json(
                'PKList', 'children', model=Feature, pks=obj._children_pks),
            self.field_to_json(
                'PKList', 'row_children', model=Feature,
                pks=obj.row_children_pks),
            ('row_children_pks', obj.row_children_pks),
            ('page_children_pks', obj.page_children_pks),
            ('descendant_pks', obj._descendant_pks),
            ('row_descendant_pks', obj.row_descendant_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def feature_v1_loader(self, pk):
        queryset = Feature.objects
        try:
            obj = queryset.get(pk=pk)
        except Feature.DoesNotExist:
            return None
        else:
            self.feature_v1_add_related_pks(obj)
            return obj

    def feature_v1_add_related_pks(self, obj):
        """Add related primary keys to a Feature instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
        if not hasattr(obj, '_children_pks'):
            obj._children_pks = [
                child_pk for child_pk, _ in obj._child_pks_and_is_page]
        if not hasattr(obj, '_reference_pks'):
            obj._reference_pks = sorted(
                obj.references.values_list('pk', flat=True))
        if not hasattr(obj, '_support_pks'):
            obj._support_pks = sorted(
                obj.supports.values_list('pk', flat=True))
        if not hasattr(obj, '_descendant_pks'):
            if obj.descendant_count <= settings.PAGINATE_VIEW_FEATURE:
                obj._descendant_pks = obj.descendant_pks
            else:
                obj._descendant_pks = []

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
        self.maturity_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('name', obj.name),
            self.field_to_json(
                'PKList', 'specifications', model=Specification,
                pks=obj._specification_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def maturity_v1_loader(self, pk):
        queryset = Maturity.objects
        try:
            obj = queryset.get(pk=pk)
        except Maturity.DoesNotExist:
            return None
        else:
            self.maturity_v1_add_related_pks(obj)
            return obj

    def maturity_v1_add_related_pks(self, obj):
        """Add related primary keys to a Maturity instance."""
        if not hasattr(obj, '_specification_pks'):
            obj._specification_pks = sorted(
                obj.specifications.values_list('pk', flat=True))
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

    def maturity_v1_invalidator(self, obj):
        return []

    def reference_v1_serializer(self, obj):
        """Serialize Reference instance to plain dictionary."""
        if not obj:
            return None
        self.reference_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('note', obj.note),
            self.field_to_json(
                'PK', 'section', model=Section, pk=obj.section_id),
            self.field_to_json(
                'PK', 'feature', model=Feature, pk=obj.feature_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def reference_v1_loader(self, pk):
        """Load a Reference instance by primary key."""
        try:
            obj = Reference.objects.get(pk=pk)
        except Reference.DoesNotExist:
            return None
        else:
            self.reference_v1_add_related_pks(obj)
            return obj

    def reference_v1_add_related_pks(self, obj):
        """Cache related objects on a Reference instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

    def reference_v1_invalidator(self, obj):
        """Identify instance caches related to this Reference instance."""
        return [
            ('Section', obj.section_id, False),
            ('Feature', obj.feature_id, False),
        ]

    def section_v1_serializer(self, obj):
        """Serialize Section instance to plain dictionary."""
        # TODO bug 1216786: remove dropped fields note, features
        if not obj:
            return None
        self.section_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('number', obj.number),
            ('name', obj.name),
            ('subpath', obj.subpath),
            self.field_to_json(
                'PK', 'specification', model=Specification,
                pk=obj.specification_id),
            self.field_to_json(
                'PKList', 'references', model=Reference,
                pks=obj._reference_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def section_v1_loader(self, pk):
        queryset = Section.objects
        try:
            obj = queryset.get(pk=pk)
        except Section.DoesNotExist:
            return None
        else:
            self.section_v1_add_related_pks(obj)
            return obj

    def section_v1_add_related_pks(self, obj):
        """Add related primary keys to a Section instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
        if not hasattr(obj, '_reference_pks'):
            obj._reference_pks = sorted(
                obj.references.values_list('pk', flat=True))

    def section_v1_invalidator(self, obj):
        return [('Specification', obj.specification_id, False)]

    def specification_v1_serializer(self, obj):
        if not obj:
            return None
        self.specification_v1_add_related_pks(obj)
        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('mdn_key', obj.mdn_key),
            ('name', obj.name),
            ('uri', obj.uri),
            self.field_to_json(
                'PKList', 'sections', model=Section, pks=obj._section_pks),
            self.field_to_json(
                'PK', 'maturity', model=Maturity, pk=obj.maturity_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def specification_v1_loader(self, pk):
        queryset = Specification.objects
        try:
            obj = queryset.get(pk=pk)
        except Specification.DoesNotExist:
            return None
        else:
            self.specification_v1_add_related_pks(obj)
            return obj

    def specification_v1_add_related_pks(self, obj):
        """Add related primary keys to a Specification instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
        if not hasattr(obj, '_section_pks'):
            obj._section_pks = list(
                obj.sections.values_list('pk', flat=True))

    def specification_v1_invalidator(self, obj):
        return [('Maturity', obj.maturity_id, False)]

    def support_v1_serializer(self, obj):
        if not obj:
            return None
        self.support_v1_add_related_pks(obj)
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
            self.field_to_json(
                'PK', 'version', model=Version, pk=obj.version_id),
            self.field_to_json(
                'PK', 'feature', model=Feature, pk=obj.feature_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def support_v1_loader(self, pk):
        queryset = Support.objects
        try:
            obj = queryset.get(pk=pk)
        except Support.DoesNotExist:
            return None
        else:
            self.support_v1_add_related_pks(obj)
            return obj

    def support_v1_add_related_pks(self, obj):
        """Add related primary keys to a Support instance."""
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

    def support_v1_invalidator(self, obj):
        return [
            ('Version', obj.version_id, True),
            ('Feature', obj.feature_id, True),
        ]

    def version_v1_serializer(self, obj):
        if not obj:
            return None
        self.version_v1_add_related_pks(obj)
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
                'PKList', 'supports', model=Support, pks=obj._support_pks),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=obj._history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=obj._history_pks[0]),
        ))

    def version_v1_loader(self, pk):
        queryset = Version.objects
        try:
            obj = queryset.get(pk=pk)
        except Version.DoesNotExist:
            return None
        else:
            self.version_v1_add_related_pks(obj)
            return obj

    def version_v1_add_related_pks(self, obj):
        """Add related primary keys to a Version instance."""
        if not hasattr(obj, '_support_pks'):
            obj._support_pks = sorted(
                obj.supports.values_list('pk', flat=True))
        if not hasattr(obj, '_history_pks'):
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))

    def version_v1_invalidator(self, obj):
        return [
            ('Browser', obj.browser_id, True)]

    def user_v1_serializer(self, obj):
        if not obj or not obj.is_active:
            return None
        self.user_v1_add_related_pks(obj)
        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
            ('group_names', obj.group_names),
            self.field_to_json(
                'PKList', 'changesets', model=Changeset,
                pks=obj._changeset_pks),
        ))

    def user_v1_add_related_pks(self, obj):
        """Add related primary keys and data to a User instance."""
        if not hasattr(obj, 'group_names'):
            obj.group_names = sorted(obj.groups.values_list('name', flat=True))
        if not hasattr(obj, '_changeset_pks'):
            obj._changeset_pks = list(
                obj.changesets.values_list('pk', flat=True))

    def user_v1_loader(self, pk):
        try:
            obj = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None
        else:
            self.user_v1_add_related_pks(obj)
            return obj

    def user_v1_invalidator(self, obj):
        return []

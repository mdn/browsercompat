"""Customize filters for the API."""
from rest_framework.filters import DjangoFilterBackend


class UnorderedDjangoFilterBackend(DjangoFilterBackend):
    """DjangoFilterBackend without ordering."""

    def get_filter_class(self, view, queryset=None):
        """
        Return the django-filters `FilterSet` used to filter the queryset.

        Same as DjangoFilterBackend.get_filter_class, but asserts filter_class
        is never set, and sets order_by is False.
        """
        filter_class = getattr(view, 'filter_class', None)
        filter_fields = getattr(view, 'filter_fields', None)
        assert not filter_class

        if filter_fields:  # pragma: no cover
            class AutoFilterSet(self.default_filter_set):
                class Meta:
                    model = queryset.model
                    fields = filter_fields
                    order_by = False
            return AutoFilterSet

        return None  # pragma: no cover

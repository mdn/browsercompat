# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django_extensions.db.fields.json import JSONField
from mptt.models import MPTTModel, TreeForeignKey
from simple_history import register
from simple_history.models import HistoricalRecords

from .validators import LanguageDictValidator, SecureURLValidator


@python_2_unicode_compatible
class Browser(models.Model):
    '''A browser or other web client'''
    slug = models.SlugField(unique=True)
    icon = models.URLField(blank=True, validators=[SecureURLValidator()])
    name = JSONField(validators=[LanguageDictValidator()])
    note = JSONField(
        blank=True, null=True, validators=[LanguageDictValidator()])
    history = HistoricalRecords()

    def __str__(self):
        return self.slug


@python_2_unicode_compatible
class Version(models.Model):
    '''A version of a browser'''
    STATUS_CHOICES = [(k, k) for k in (
        'unknown',
        'current',
        'future',
        'retired',
        'beta',
        'retired beta',
    )]

    browser = models.ForeignKey(Browser, related_name='versions')
    version = models.CharField(blank=True, max_length=20)
    release_day = models.DateField(blank=True, null=True)
    retirement_day = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='unknown')
    release_notes_uri = JSONField(blank=True)
    note = JSONField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{0} {1}".format(self.browser, self.version)

    class Meta:
        order_with_respect_to = 'browser'


@python_2_unicode_compatible
class Feature(MPTTModel):
    '''A web technology'''

    slug = models.SlugField(
        help_text="Unique, human-friendly slug.",
        unique=True, blank=False)
    mdn_path = models.CharField(
        help_text=(
            "The path to the page on MDN that this feature was first"
            " scraped from.  May be used in UX or for debugging import"
            " scripts."),
        blank=True, max_length=255)
    experimental = models.BooleanField(
        help_text=(
            "True if a feature is considered experimental, such as being"
            " non-standard or part of an non-ratified spec."),
        default=False)
    standardized = models.BooleanField(
        help_text=(
            "True if a feature is described in a standards-track spec,"
            " regardless of the spec’s maturity."),
        default=True)
    stable = models.BooleanField(
        help_text=(
            "True if a feature is considered suitable for production"
            " websites."),
        default=True)
    obsolete = models.BooleanField(
        help_text=(
            "True if a feature should not be used in new development."),
        default=False)
    name = JSONField(
        help_text="Feature name, in canonical or localized form.",
        blank=True, validators=[LanguageDictValidator()])
    parent = TreeForeignKey(
        'self', help_text="Feature set that contains this feature",
        null=True, blank=True, related_name='children')

    @property
    def ancestors(self):
        return self.get_ancestors(include_self=True)

    @property
    def siblings(self):
        return self.get_siblings(include_self=True)

    @property
    def descendants(self):
        return self.get_descendants(include_self=True)

    def __str__(self):
        return self.slug


# Must be done after class declaration due to coordination with MPTT
# https://github.com/treyhunner/django-simple-history/issues/87
register(Feature)

#
# Cache invalidation signals
#

cached_model_names = (
    'Browser', 'Feature', 'Version', 'User', 'HistoricalBrowser')


@receiver(post_save, dispatch_uid='post_save_update_cache')
def post_save_update_cache(sender, instance, created, raw, **kwargs):
    if raw:
        return
    name = sender.__name__
    if name in cached_model_names:
        from .tasks import update_cache_for_instance
        update_cache_for_instance(name, instance.pk, instance)


@receiver(post_delete, dispatch_uid='post_delete_update_cache')
def post_delete_update_cache(sender, instance, **kwargs):
    name = sender.__name__
    if name in cached_model_names:
        from .tasks import update_cache_for_instance
        update_cache_for_instance(name, instance.pk, instance)

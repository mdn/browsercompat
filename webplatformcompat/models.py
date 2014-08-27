# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django_extensions.db.fields.json import JSONField
from simple_history.models import HistoricalRecords

from .validators import LanguageDictValidator, SecureURLValidator


@python_2_unicode_compatible
class Browser(models.Model):
    slug = models.SlugField(unique=True)
    icon = models.URLField(blank=True, validators=[SecureURLValidator()])
    name = JSONField(validators=[LanguageDictValidator()])
    note = JSONField(
        blank=True, null=True, validators=[LanguageDictValidator()])
    history = HistoricalRecords()

    def __str__(self):
        return self.slug


@python_2_unicode_compatible
class BrowserVersion(models.Model):
    STATUS_CHOICES = [(k, k) for k in (
        'unknown',
        'current',
        'future',
        'retired',
        'beta',
        'retired beta',
    )]

    browser = models.ForeignKey(Browser, related_name='browser_versions')
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

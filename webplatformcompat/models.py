# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django_extensions.db.fields.json import JSONField
from simple_history.models import HistoricalRecords

from .validators import SecureURLValidator, LanguageDictValidator


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
    STATUS_UNKNOWN = 0
    STATUS_CURRENT = 1
    STATUS_FUTURE = 3
    STATUS_RETIRED = 4
    STATUS_BETA = 5
    STATUS_RETIRED_BETA = 6
    STATUS_CHOICES = (
        (STATUS_UNKNOWN, 'unknown'),
        (STATUS_CURRENT, 'current'),
        (STATUS_FUTURE, 'future'),
        (STATUS_RETIRED, 'retired'),
        (STATUS_BETA, 'beta'),
        (STATUS_RETIRED_BETA, 'retired beta'),
    )

    browser = models.ForeignKey(Browser)
    version = models.CharField(blank=True, max_length=10)
    release_day = models.DateField(blank=True, null=True)
    retirement_day = models.DateField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    release_notes_uri = JSONField(blank=True)
    note = JSONField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{0} {1}".format(self.browser, self.version)

# -*- coding: utf-8 -*-

from django.db import models


class Browser(models.Model):
    slug = models.SlugField(unique=True)
    icon = models.URLField(blank=True)
    name = models.CharField(max_length=50)
    note = models.TextField(blank=True)


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
    version = models.CharField(max_length=10)
    release_day = models.DateField(blank=True, null=True)
    retirement_day = models.DateField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    icon = models.URLField(blank=True)

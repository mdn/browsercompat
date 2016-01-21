# -*- coding: utf-8 -*-
"""Remove non-English TranslatedContent.

Localized content is stored for the purpose of parsing compatiblity data for
structured cotnent. After working on the MDN importer for many months, it
feels that parsing is the wrong method for extracting the non-English
localized content:

* The HTML and KumaScript on localized pages may also be broken, requiring
  a multiple of the effort used to clean up English pages,
* Some localized pages are well behind the English page, and contain
  significantly different content, and
* When the content is in sync, there is no strong identifier linking strings
  on the localized variant to the English variant.

For these reasons, a different tool should be used to assist a translator in
migrating localized strings to the data store, rather than try to automate
the migration. Dropping the unused data from the database, to reduce the size.
"""
from __future__ import unicode_literals, print_function

from django.db import migrations


def remove_content(apps, schema_editor):
    TranslatedContent = apps.get_model('mdn', 'TranslatedContent')
    TranslatedContent.objects.exclude(locale='en-US').delete()


def download_content(apps, schema_editor):
    print('\nReset importer pages to re-download non-English content.')


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0009_switch_feature_to_1to1'),
    ]

    operations = [
        migrations.RunPython(remove_content, download_content)
    ]

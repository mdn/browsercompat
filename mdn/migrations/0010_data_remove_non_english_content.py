# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import migrations


def remove_content(apps, schema_editor):
    TranslatedContent = apps.get_model("mdn", "TranslatedContent")
    TranslatedContent.objects.exclude(locale='en-US').delete()


def download_content(apps, schema_editor):
    print("\nReset importer pages to re-download non-English content.")


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0009_switch_feature_to_1to1'),
    ]

    operations = [
        migrations.RunPython(remove_content, download_content)
    ]

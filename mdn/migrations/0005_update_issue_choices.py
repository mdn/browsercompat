# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0004_expand_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='slug',
            field=models.SlugField(choices=[('spec_h2_name', 'spec_h2_name'), ('doc_parse_error', 'doc_parse_error'), ('compatgeckofxos_unknown', 'compatgeckofxos_unknown'), ('second_footnote', 'second_footnote'), ('spec2_converted', 'spec2_converted'), ('compatgeckofxos_override', 'compatgeckofxos_override'), ('unknown_spec', 'unknown_spec'), ('spec2_wrong_kumascript', 'spec2_wrong_kumascript'), ('specname_converted', 'specname_converted'), ('footnote_no_id', 'footnote_no_id'), ('extra_cell', 'extra_cell'), ('inline_text', 'inline_text'), ('unknown_version', 'unknown_version'), ('failed_download', 'failed_download'), ('bad_json', 'bad_json'), ('spec_h2_id', 'spec_h2_id'), ('skipped_h3', 'skipped_h3'), ('exception', 'exception'), ('false_start', 'false_start'), ('footnote_missing', 'footnote_missing'), ('unknown_kumascript', 'unknown_kumascript'), ('compatgeckodesktop_unknown', 'compatgeckodesktop_unknown'), ('specname_blank_key', 'specname_blank_key'), ('halt_import', 'halt_import'), ('specname_not_kumascript', 'specname_not_kumascript'), ('feature_header', 'feature_header'), ('spec_mismatch', 'spec_mismatch'), ('tag_dropped', 'tag_dropped'), ('section_skipped', 'section_skipped'), ('section_missed', 'section_missed'), ('missing_attribute', 'missing_attribute'), ('unexpected_attribute', 'unexpected_attribute'), ('spec2_arg_count', 'spec2_arg_count'), ('footnote_unused', 'footnote_unused'), ('footnote_feature', 'footnote_feature'), ('nested_p', 'nested_p'), ('footnote_multiple', 'footnote_multiple'), ('unknown_browser', 'unknown_browser'), ('specdesc_spec2_invalid', 'specdesc_spec2_invalid')], help_text='Human-friendly slug for issue.'),
            preserve_default=True,
        ),
    ]

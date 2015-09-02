# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mdn', '0005_update_issue_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='slug',
            field=models.SlugField(help_text='Human-friendly slug for issue.', choices=[('bad_json', 'bad_json'), ('cell_out_of_bounds', 'cell_out_of_bounds'), ('compatgeckodesktop_unknown', 'compatgeckodesktop_unknown'), ('compatgeckofxos_override', 'compatgeckofxos_override'), ('compatgeckofxos_unknown', 'compatgeckofxos_unknown'), ('exception', 'exception'), ('extra_cell', 'extra_cell'), ('failed_download', 'failed_download'), ('feature_header', 'feature_header'), ('footnote_feature', 'footnote_feature'), ('footnote_gap', 'footnote_gap'), ('footnote_missing', 'footnote_missing'), ('footnote_multiple', 'footnote_multiple'), ('footnote_no_id', 'footnote_no_id'), ('footnote_unused', 'footnote_unused'), ('halt_import', 'halt_import'), ('inline_text', 'inline_text'), ('kumascript_wrong_args', 'kumascript_wrong_args'), ('missing_attribute', 'missing_attribute'), ('no_data', 'no_data'), ('skipped_content', 'skipped_content'), ('skipped_h3', 'skipped_h3'), ('spec2_converted', 'spec2_converted'), ('spec2_omitted', 'spec2_omitted'), ('spec_h2_id', 'spec_h2_id'), ('spec_h2_name', 'spec_h2_name'), ('spec_mismatch', 'spec_mismatch'), ('specname_blank_key', 'specname_blank_key'), ('specname_converted', 'specname_converted'), ('specname_not_kumascript', 'specname_not_kumascript'), ('specname_omitted', 'specname_omitted'), ('tag_dropped', 'tag_dropped'), ('unexpected_attribute', 'unexpected_attribute'), ('unexpected_kumascript', 'unexpected_kumascript'), ('unknown_browser', 'unknown_browser'), ('unknown_kumascript', 'unknown_kumascript'), ('unknown_spec', 'unknown_spec'), ('unknown_version', 'unknown_version')]),
            preserve_default=True,
        ),
    ]

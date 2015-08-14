# -*- coding: utf-8 -*-
"""Issues that can be found while scraping MDN pages."""

from __future__ import unicode_literals
from collections import OrderedDict

# Issue severity
WARNING = 1
ERROR = 2
CRITICAL = 3
SEVERITIES = {
    WARNING: 'Warning',
    ERROR: 'Error',
    CRITICAL: 'Critical',
}

# Issue slugs, severity, brief templates, and long templates
# This was a database model, but it was cumbersome to update text with a
#  database migration, and changing slugs require code changes as well.
ISSUES = OrderedDict((
    ('bad_json', (
        CRITICAL,
        'Response from {url} is not JSON',
        'Actual content:\n{content}')),
    ('cell_out_of_bounds', (
        ERROR,
        'Cell ranges outside of the compatibility table',
        'The cell expands past the bounds of the compatibility table. If it'
        ' has a rowspan or colspan, in-bound cells will be applied.')),
    ('compatgeckodesktop_unknown', (
        ERROR,
        'Unknown Gecko version "{version}"',
        'The importer does not recognize this version for CompatGeckoDesktop.'
        ' Change the MDN page or update the importer.')),
    ('compatgeckofxos_override', (
        ERROR,
        'Override "{override}" is invalid for Gecko version "{version}".',
        'The importer does not recognize this override for CompatGeckoFxOS.'
        ' Change the MDN page or update the importer.')),
    ('compatgeckofxos_unknown', (
        ERROR,
        'Unknown Gecko version "{version}"',
        'The importer does not recognize this version for CompatGeckoFxOS.'
        ' Change the MDN page or update the importer.')),
    ('doc_parse_error', (
        CRITICAL,
        'No imported data due to unexpected page structure.',
        'The importer was unable to handle the page structure enough to'
        ' determine if there was compatibility data.')),
    ('exception', (CRITICAL, 'Unhandled exception', '{traceback}')),
    ('extra_cell', (
        ERROR,
        'Extra cell in compatibility table row.',
        'A row in the compatibility table has more cells than the header'
        ' row. It may be the cell identified in the context, a different'
        ' cell in the row, or a missing header cell.')),
    ('failed_download', (
        CRITICAL, 'Failed to download {url}.',
        'Status {status}, Content:\n{content}')),
    ('false_start', (
        CRITICAL,
        'No <h2> found in page.',
        'A compatibility table must be after a proper <h2> to be imported.')),
    ('feature_header', (
        WARNING,
        'Expected first header to be "Feature"',
        'The first header is "{header}", not "Feature"')),
    ('footnote_feature', (
        ERROR,
        'Footnotes are not allowed on features',
        'The Feature model does not include a notes field. Remove the'
        ' footnote from the feature.')),
    ('footnote_gap', (
        ERROR,
        'There are unexpected elements in the footnote section',
        'The footnotes parser expects only <p> and <pre> sections in the'
        ' footnotes. Check for incorrect <div> wrapping and other issues.')),
    ('footnote_missing', (
        ERROR,
        'Footnote [{footnote_id}] not found.',
        'The compatibility table has a reference to footnote'
        ' "{footnote_id}", but no matching footnote was found. This may'
        ' be due to parse issues in the footnotes section, a typo in the MDN'
        ' page, or a footnote that was removed without removing the footnote'
        ' reference from the table.')),
    ('footnote_multiple', (
        ERROR,
        'Only one footnote allowed per compatibility cell.',
        'The API supports only one footnote per support assertion. Combine'
        ' footnotes [{prev_footnote_id}] and [{footnote_id}], or remove'
        ' one of them.')),
    ('footnote_no_id', (
        ERROR,
        'Footnote has no ID.',
        'Footnote references, such as [1], are used to link the footnote to'
        ' the support assertion in the compatibility table. Reformat the MDN'
        ' page to use footnote references.')),
    ('footnote_unused', (
        ERROR,
        'Footnote [{footnote_id}] is unused.',
        'No cells in the compatibility table included the footnote reference'
        ' [{footnote_id}]. This could be due to a issue importing the'
        ' compatibility cell, a typo on the MDN page, or an extra footnote'
        ' that should be removed from the MDN page.')),
    ('halt_import', (
        CRITICAL,
        'Unable to finish importing MDN page.',
        'The importer was unable to finish parsing the MDN page. This may be'
        ' due to an unknown HTML tag, nested <code> or <pre> elements, or'
        ' other unexpected content.')),
    ('inline_text', (
        ERROR,
        'Unknown inline support text "{text}".',
        'The API schema does not include inline notes. This text needs to be'
        ' converted to a footnote, converted to a support attribute (which'
        ' may require an importer update), or removed.')),
    ('kumascript_wrong_args', (
        ERROR,
        'Bad argument count in KumaScript {kumascript} in {scope}.',
        'The importer expected {name} to have {arg_spec}, but it had'
        ' {arg_count}')),
    ('nested_p', (
        ERROR,
        'Nested <p> tags are not supported.',
        'Edit the MDN page to remove the nested <p> tag')),
    ('no_data', (
        CRITICAL,
        'No data was extracted from the page.',
        'The page appears to have data, but nothing was extracted. Check for'
        ' header sections wrapped in a <div> or other element. (Context'
        ' will probably not highlight the issue)')),
    ('missing_attribute', (
        ERROR,
        'The tag <{node_type}> is missing the expected attribute {ident}',
        'Add the missing attribute or convert the tag to plain text.')),
    ('second_footnote', (
        ERROR,
        'An additional footnote was detected in content',
        'The footnote [{original}] is being used, and the footnote [{new}]'
        ' discarded.  If footnotes are in the same <p> and split by <br>'
        ' tags, then split into paragraphs to fix.')),
    ('section_skipped', (
        CRITICAL,
        'Section <h2>{title}</h2> has unexpected content.',
        'The parser was trying to match rule "{rule_name}", but was unable to'
        ' understand some unexpected content. This may be markup or'
        ' text, or a side-effect of previous issues. Look closely at the'
        ' context (as well as any previous issues) to find the problem'
        ' content.')),
    ('section_missed', (
        CRITICAL,
        'Section <h2>{title}</h2> was not imported.',
        'The import of section {title} failed, but no parse error was'
        ' detected. This is usually because of a previous critical error,'
        ' which must be cleared before any parsing can be attempted.')),
    ('skipped_content', (
        WARNING,
        'Content will not be imported.',
        'This content will not be imported into the API.')),
    ('skipped_h3', (
        WARNING,
        '<h3>{h3}</h3> was not imported.',
        '<h3> subsections are usually prose compatibility information, and'
        ' anything after an <h3> is not parsed or imported. Convert to'
        ' footnotes or move to a different <h2> section.')),
    ('spec_h2_id', (
        WARNING,
        'Expected <h2 id="Specifications">, actual id={h2_id}',
        'Fix the id so that the table of contents, other feature work.')),
    ('spec_h2_name', (
        WARNING,
        'Expected <h2 name="Specifications">, actual name={h2_name}',
        'Fix or remove the name attribute.')),
    ('spec_mismatch', (
        ERROR,
        'SpecName({specname_key}, ...) does not match'
        ' Spec2({spec2_key}).',
        'SpecName and Spec2 must refer to the same mdn_key. Update the MDN'
        ' page.')),
    ('specname_blank_key', (
        ERROR,
        'KumaScript SpecName has a blank key',
        'Update the MDN page to include a valid mdn_key')),
    ('specname_converted', (
        WARNING,
        'Specification name should be converted to KumaScript',
        'The specification "{original}" should be replaced with the KumaScript'
        ' {{{{SpecName({key})}}}}')),
    ('specname_not_kumascript', (
        ERROR,
        'Specification name unknown, and should be converted to KumaScript',
        'Expected KumaScript {{{{SpecName(key, subpath, name)}}}}, but got'
        ' text "{original}".')),
    ('specname_omitted', (
        WARNING,
        'Expected KumaScript SpecName(), got nothing',
        'Expected KumaScript {{{{SpecName(key, subpath, name)}}}}, but got'
        ' no text. Fix or remove empty table row.')),
    ('spec2_wrong_kumascript', (
        ERROR,
        'Expected KumaScript Spec2(), got {kumascript}',
        'Change to Spec2(mdn_key), using the mdn_key from the SpecName()'
        ' KumaScript.')),
    ('spec2_converted', (
        WARNING,
        'Specification status should be converted to KumaScript',
        'Expected KumaScript {{{{Spec2("{key}")}}}}, but got text'
        ' "{original}".')),
    ('spec2_omitted', (
        WARNING,
        'Expected KumaScript Spec2(), got nothing',
        'Change to Spec2(mdn_key), using the mdn_key from the SpecName()'
        ' KumaScript, or remove empty table row.')),
    ('specdesc_spec2_invalid', (
        ERROR,
        '{kumascript} is invalid in the spec description',
        'Handled as if {{{{SpecName(...)}}}} was used. Update the MDN page.')),
    ('tag_dropped', (
        WARNING,
        'HTML element {tag} (but not wrapped content) was removed.',
        'The element {tag} is not allowed in the {scope} scope, and was'
        ' removed. You can remove the tag from the MDN page to remove the'
        ' warning.')),
    ('unexpected_attribute', (
        WARNING,
        'Unexpected attribute <{node_type} {ident}="{value}">',
        'For <{node_type}>, the importer expects {expected}. This unexpected'
        ' attribute will be discarded.')),
    ('unknown_browser', (
        ERROR,
        'Unknown Browser "{name}".',
        'The API does not have a browser with the name "{name}".'
        ' This could be a typo on the MDN page, or the browser needs to'
        ' be added to the API.')),
    ('unknown_kumascript', (
        ERROR,
        'Unknown KumaScript {kumascript} in {scope}.',
        'The importer has to run custom code to import KumaScript, and it'
        ' hasn\'t been taught how to import {name} when it appears in a'
        ' {scope}. File a bug, or convert the MDN page to not use this'
        ' KumaScript macro.')),
    ('unknown_spec', (
        ERROR,
        'Unknown Specification "{key}".',
        'The API does not have a specification with mdn_key "{key}".'
        ' This could be a typo on the MDN page, or the specification needs to'
        ' be added to the API.')),
    ('unknown_version', (
        ERROR,
        'Unknown version "{version}" for browser "{browser_name}"',
        'The API does not have the version "{version}" for browser'
        ' "{browser_name}" (id {browser_id}, slug "{browser_slug}").'
        ' This could be a typo on the MDN page, or the version needs to'
        ' be added to the API.')),
))

UNKNOWN_ISSUE = (
    CRITICAL, 'Unknown Issue', "This issue slug doesn't have a description.")

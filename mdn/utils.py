# coding: utf-8
"""Utility functions for MDN parsing."""
from __future__ import unicode_literals

from django.utils.six import text_type
import string


def date_to_iso(date):
    """Convert a datetime.Date to the ISO 8601 format, or None."""
    if date:
        return date.isoformat()
    else:
        return None


def end_of_line(text, pos):
    """Get the position of the end of the line from pos."""
    try:
        return text.index('\n', pos)
    except ValueError:
        return len(text)


def format_version(version):
    """Format a version to 1.0, 1.0.1, etc."""
    if '.' in version:
        return version
    else:
        assert version
        assert int(version)
        return version + '.0'


def is_new_id(_id):
    """Detect if an ID signifies a new resource.

    New resource IDs are text strings prefixed with an underscore.
    """
    return isinstance(_id, text_type) and _id[0] == '_'


def join_content(content_bits):
    """Construct a string with just the right whitespace."""
    out = ''
    nospace_before = '!,.;?[ '
    nospace_after = ' '
    for bit in content_bits:
        if bit:
            if (out and out[-1] not in nospace_after and
                    bit[0] not in nospace_before):
                out += ' '
            out += bit
    return out


def normalize_name(name):
    """Normalize a name for IDs, slugs."""
    to_remove = ('<code>', '</code>', '&lt;', '&gt;')
    normalized_name = name.lower()
    for removal in to_remove:
        normalized_name = normalized_name.replace(removal, '')
    return normalized_name


def slugify(word, length=50, suffix=''):
    """Create a slugged version of a word or phrase."""
    raw = word.lower()
    out = []
    acceptable = string.ascii_lowercase + string.digits + '_-'
    for c in raw:
        if c in acceptable:
            out.append(c)
        else:
            out.append('_')
    slugged = ''.join(out)
    while '__' in slugged:
        slugged = slugged.replace('__', '_')
    if slugged.endswith('_') and len(slugged) > 1:
        slugged = slugged[:-1]
    suffix = text_type(suffix) if suffix else ''
    with_suffix = slugged[slice(length - len(suffix))] + suffix
    return with_suffix

# coding: utf-8
"""Utility functions for MDN parsing."""
from __future__ import unicode_literals


def join_content(content_bits):
    """Construct a string with just the right whitespace."""
    out = ""
    nospace_before = '!,.;? '
    nospace_after = ' '
    for bit in content_bits:
        if bit:
            if (out and out[-1] not in nospace_after and
                    bit[0] not in nospace_before):
                out += " "
            out += bit
    return out

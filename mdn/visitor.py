# coding: utf-8
"""Base classes for content scraping / visiting."""

from parsimonious.nodes import NodeVisitor

from .data import Data
from .issues import ISSUES


class Extractor(object):
    """Extracts information from parsed HTML."""

    def initialize_extractor(self, offset=0, data=None):
        """Setup common variables.

        offset - The character position that this fragment starts at.
        issues - The collected issues found during extraction.
        """
        self.offset = offset
        self.data = data or Data()
        self.issues = []

    def add_issue(self, issue_slug, processed, **issue_args):
        """Add an issue for a given processed node."""
        assert issue_slug in ISSUES
        self.issues.append(
            (issue_slug, processed.start, processed.end, issue_args))

    def add_raw_issue(self, issue):
        """Add an issue in tuple (slug, start, end, args) format."""
        issue_slug, start, end, issue_args = issue
        assert issue_slug in ISSUES
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert end >= start
        assert hasattr(issue_args, 'keys')
        self.issues.append(issue)


class Visitor(Extractor, NodeVisitor):
    """Base class for node vistors."""
    def __init__(self, offset=0, data=None):
        super(Visitor, self).__init__()
        self.initialize_extractor(offset=offset, data=data)

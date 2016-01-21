# coding: utf-8
"""Base classes for content scraping / visiting."""
from __future__ import print_function, unicode_literals

from parsimonious.nodes import NodeVisitor

from .data import Data
from .issues import ISSUES


class Recorder(object):
    """Records information in HTML or parsed HTML."""

    def initialize_tracker(self, offset=0, data=None):
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


class Visitor(Recorder, NodeVisitor):
    """Base class for node vistors.

    The Parsimonious NodeVisitor works from leaf nodes up to trunk nodes.
    """

    def __init__(self, offset=0, data=None):
        super(Visitor, self).__init__()
        self.initialize_tracker(offset=offset, data=data)


class Extractor(Recorder):
    """Extracts information from parsed HTML.

    The Extractor works from trunk nodes to leaf nodes.
    """

    extractor_name = 'Extractor'

    def initialize_extractor(self, elements=None, debug=False, **kwargs):
        """Setup extractor plus common variables."""
        self.initialize_tracker(**kwargs)
        self.elements = elements or []
        self.debug = debug

    def extract(self):
        """Extract data from a parsed list of elements.

        This is used when you need sibling processing of a tree, rather than
        subtree processing during parsing.
        """
        self.setup_extract()
        state = 'begin'
        for element in self.elements:
            state = self.walk(state, element)
        return self.extracted_data()

    def setup_extract(self):
        """Setup the extraction state variables."""
        raise NotImplementedError(
            '.setup_extract method is not implemented')  # pragma: no cover

    def walk(self, state, element):
        """
        Walk a parsed element.

        Keyword Attributes:
        state - A string specifying the current state
        element - The element being walked

        Return is the new state
        """
        old_state = state
        state, recurse = self.entering_element(state, element)
        if state != old_state:
            self.report_transition('entering', element, old_state, state)
        if recurse and hasattr(element, 'children'):
            for child in element.children:
                state = self.walk(state, child)
        old_state = state
        state = self.leaving_element(state, element)
        if state != old_state:
            self.report_transition('leaving', element, old_state, state)
        return state

    def report_transition(self, phase, element, old_state, new_state):
        """Report transitions, for debugging."""
        if self.debug:  # pragma: no cover
            print('In {}, state changed from "{}" to "{}" when {} {}'.format(
                self.extractor_name, old_state, new_state, phase, element))

    def entering_element(self, state, element):
        """
        Extract data (state or information) from entering an element.

        Return is a tuple of:
            - The next state
            - True if the element's children should be walked for extraction.
        """
        raise NotImplementedError(
            '.entering_element method is not implemented')  # pragma: no cover

    def leaving_element(self, state, element):
        """
        Extract data (state or information) from leaving an element.

        Return is the next state.
        """
        raise NotImplementedError(
            '.leaving_element method is not implemented')  # pragma: no cover

    def extracted_data(self):
        """
        Finalize the extracted data.

        Return is a dictionary of data items.
        """
        raise NotImplementedError(
            '.extracted_data method is not implemented')  # pragma: no cover

    def is_tag(self, element, tag):
        """Return True if element matches the tag."""
        return getattr(element, 'tag', None) == tag

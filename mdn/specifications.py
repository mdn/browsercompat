# coding: utf-8
"""Parser for Specification section of an MDN raw page."""

from .html import HnElement, HTMLElement, HTMLText
from .kumascript import (
    KumaScript, KumaVisitor, SpecName, Spec2, kumascript_grammar)
from .utils import join_content
from .visitor import Extractor


class SpecSectionExtractor(Extractor):
    """Extracts data from elements representing a Specifications section.

    A specification section looks like:

    <h2 name="Specifications" id="Specifications">Specifications</h2>
    <table class="standard-table">
      <thead>
        <tr>
          <th scope="col">Specification</th>
          <th scope="col">Status</th>
          <th scope="col">Comment</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{SpecName('CSS3 Backgrounds', '#the-background-size',
                         'background-size')}}</td>
          <td>{{Spec2('CSS3 Backgrounds')}}</td>
          <td>A note about this specification.</td>
        </tr>
      </tbody>
    </table>

    Non-table content raises an issue, unless it is wrapped in a
    {{WhyNoSpecStart}}/{{WhyNoSpecEnd}} pair.
    """

    extractor_name = 'Specifications Extractor'

    def __init__(self, **kwargs):
        self.initialize_extractor(**kwargs)

    def setup_extract(self):
        self.specs = []
        self.key = None
        self.spec_id = None
        self.path = None
        self.name = None
        self.spec2_key = None
        self.desc = None
        self.section_id = None

    def entering_element(self, state, element):
        if state == 'begin':
            assert isinstance(element, HnElement)
            self.extract_header(element)
            return 'extracted_header', False
        elif state == 'extracted_header':
            if self.is_tag(element, 'table'):
                return 'in_table', True
            elif isinstance(element, HTMLElement):
                self.extract_non_table(element)
                return 'extracted_header', False
        elif state == 'in_table':
            if self.is_tag(element, 'tr'):
                # Confirm header columns?
                return 'in_first_row', False
        elif state == 'in_table_data':
            if self.is_tag(element, 'tr'):
                self.key = None
                self.spec_id = None
                self.path = None
                self.name = None
                self.spec2_key = None
                self.section_id = None
                self.desc = None
                return 'in_data_row', True
        elif state == 'in_data_row':
            if self.is_tag(element, 'td'):
                self.extract_specname(element)
                return 'extracted_name', False
        elif state == 'extracted_name':
            if self.is_tag(element, 'td'):
                self.extract_spec2(element)
                return 'extracted_spec2', False
        elif state == 'extracted_spec2':
            if self.is_tag(element, 'td'):
                self.extract_specdesc(element)
                self.specs.append({
                    'specification.mdn_key': self.key,
                    'specification.id': self.spec_id,
                    'section.subpath': self.path,
                    'section.name': self.name,
                    'section.note': self.desc,
                    'section.id': self.section_id})
                return 'extracted_desc', False
        elif state == 'extracted_desc':
            # Warn on extra columns?
            pass
        elif state == 'extracted_table':
            if isinstance(element, HTMLElement):
                self.extract_non_table(element)
                return 'extracted_table', False
        else:  # pragma: no cover
            raise Exception('Unexpected state "{}"'.format(state))
        return state, True

    def leaving_element(self, state, element):
        if state == 'begin':  # pragma: no cover
            pass
        elif state == 'extracted_header':
            pass
        elif state == 'in_table':
            # Warn when exiting with no data found?
            pass
        elif state == 'in_first_row':
            assert self.is_tag(element, 'tr')
            return 'in_table_data'
        elif state == 'in_table_data':
            if self.is_tag(element, 'table'):
                return 'extracted_table'
        elif state in ('in_data_row', 'extracted_name', 'extracted_spec2'):
            # Error on not enough columns?
            pass
        elif state == 'extracted_desc':
            if self.is_tag(element, 'tr'):
                return 'in_table_data'
        elif state == 'extracted_table':
            pass
        else:  # pragma: no cover
            raise Exception('Unexpected state "{}"'.format(state))
        return state

    def extracted_data(self):
        return {
            'specs': self.specs,
            'issues': self.issues
        }

    def extract_header(self, header_element):
        expected = ('Specifications', 'Specification')
        attributes = header_element.open_tag.attributes.attrs
        for name, attribute in attributes.items():
            if name == 'id':
                h2_id = attribute.value
                if h2_id not in expected:
                    self.add_issue('spec_h2_id', attribute, h2_id=h2_id)
            if name == 'name':
                h2_name = attribute.value
                if h2_name not in expected:
                    self.add_issue('spec_h2_name', attribute, h2_name=h2_name)

    def extract_non_table(self, element):
        if element.to_html(drop_tag=True):
            self.add_issue('skipped_content', element)

    def extract_specname(self, td_element):
        reparsed = kumascript_grammar.parse(td_element.raw)
        visitor = SpecNameVisitor(data=self.data, offset=td_element.start)
        visitor.visit(reparsed)
        self.issues.extend(visitor.issues)
        self.key = visitor.mdn_key or ''
        if not (self.key or visitor.issues):
            self.add_issue('specname_omitted', td_element)
        if visitor.spec:
            self.spec_id = visitor.spec.id
        self.section_id = visitor.section_id or None
        self.path = visitor.subpath or ''
        self.name = visitor.section_name or ''

    def extract_spec2(self, td_element):
        reparsed = kumascript_grammar.parse(td_element.raw)
        visitor = Spec2Visitor(data=self.data, offset=td_element.start)
        visitor.visit(reparsed)
        self.issues.extend(visitor.issues)
        if visitor.mdn_key:
            # Standard Spec2 KumaScript - check for match
            spec2_key = visitor.mdn_key
            if spec2_key != self.key:
                self.add_issue(
                    'spec_mismatch', td_element, spec2_key=spec2_key,
                    specname_key=self.key)
        elif visitor.spec2_item:
            # Text like 'Standard' or non-standard KumaScript
            item = visitor.spec2_item
            if isinstance(item, HTMLText) and not isinstance(item, KumaScript):
                self.add_issue(
                    'spec2_converted', item, key=self.key,
                    original=item.cleaned)
        else:
            self.add_issue('spec2_omitted', td_element)

    def extract_specdesc(self, td_element):
        reparsed = kumascript_grammar.parse(td_element.raw)
        visitor = SpecDescVisitor(data=self.data, offset=td_element.start)
        visitor.visit(reparsed)
        self.issues.extend(visitor.issues)
        html = [item.to_html() for item in visitor.desc_items]
        self.desc = join_content(html)


class SpecNameVisitor(KumaVisitor):
    """
    Visitor for a SpecName HTML fragment.

    This is the first column of the Specifications table.
    """

    scope = 'specification name'
    _allowed_tags = ['td']

    def __init__(self, **kwargs):
        super(SpecNameVisitor, self).__init__(**kwargs)
        self.mdn_key = None
        self.subpath = None
        self.section_id = None
        self.section_name = None
        self.spec_item = None
        self.spec = None

    def process(self, cls, node, **kwargs):
        """Look for SpecName nodes."""
        processed = super(SpecNameVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, SpecName):
            assert not self.spec_item
            assert not self.mdn_key
            assert not self.subpath
            assert not self.section_name
            self.spec_item = processed
            self.mdn_key = processed.mdn_key
            self.subpath = processed.subpath
            self.section_name = processed.section_name
            self.spec = processed.spec
            self.section_id = processed.section_id
        elif isinstance(processed, KumaScript):
            pass  # Issues added by KS
        elif (isinstance(processed, HTMLText) and processed.cleaned):
            text = processed.cleaned
            legacy_specs = {
                'ECMAScript 1st Edition.': 'ES1',
                'ECMAScript 3rd Edition.': 'ES3'}
            key = legacy_specs.get(text, '')
            if key:
                self.mdn_key = key
                self.spec_item = processed
                self.add_issue(
                    'specname_converted', processed, original=text, key=key)
                self.spec = self.data.lookup_specification(key)
                if self.spec:
                    self.section_id = self.data.lookup_section_id(
                        self.spec.id, self.subpath)
                else:
                    self.add_issue('unknown_spec', self.spec_item, key=key)
            else:
                self.add_issue(
                    'specname_not_kumascript', processed, original=text)
        return processed


class Spec2Visitor(KumaVisitor):
    """
    Visitor for a Spec2 HTML fragment.

    This is the second column of the Specifications table.
    """

    scope = 'specification maturity'
    _allowed_tags = ['td']

    def __init__(self, **kwargs):
        super(Spec2Visitor, self).__init__(**kwargs)
        self.mdn_key = None
        self.spec2_item = None
        self.spec = None
        self.maturity = None

    def process(self, cls, node, **kwargs):
        """Look for Spec2 nodes."""
        processed = super(Spec2Visitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, Spec2):
            assert not self.spec2_item
            assert not self.mdn_key
            self.spec2_item = processed
            self.mdn_key = processed.mdn_key
            self.spec = processed.spec
            if self.spec:
                self.maturity = self.spec.maturity
        elif isinstance(processed, KumaScript):
            pass
        elif (isinstance(processed, HTMLText) and processed.cleaned and
                not self.mdn_key and not self.spec2_item):
            self.spec2_item = processed
        return processed


class SpecDescVisitor(KumaVisitor):
    """
    Visitor for a Specification description fragment.

    This is the third column of the Specifications table.
    """

    scope = 'specification description'
    _allowed_tags = ['a', 'br', 'code', 'td']

    def __init__(self, **kwargs):
        super(SpecDescVisitor, self).__init__(**kwargs)
        self.desc_items = None

    def process(self, cls, node, **kwargs):
        """Look for description nodes."""
        processed = super(SpecDescVisitor, self).process(
            cls, node, **kwargs)
        if isinstance(processed, HTMLElement) and processed.tag == 'td':
            assert self.desc_items is None
            self.desc_items = processed.children
        return processed

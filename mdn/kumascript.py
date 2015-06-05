# coding: utf-8
"""Parser for KumaScript used in compatibility data.

KumaScript is a macro system used on MDN:

https://github.com/mozilla/kumascript

KumaScript uses a JS-like syntax.  The source is stored as pages on MDN:

https://developer.mozilla.org/en-US/docs/Template:SpecName

KumaScript can query the database, do math, and generate text using all the
power of JavaScript.  It's slow, so it is rendered server-side and cached.
The unrendered version of a page can be accessed by asking for the raw version:

https://developer.mozilla.org/en-US/docs/Web/CSS/display
https://developer.mozilla.org/en-US/docs/Web/CSS/display?raw

The MDN importer needs to recognize KumaScript templates in the raw page, and:
1. For valid KumaScript, extract data and/or render HTML
2. For invalid KumaScript, generate an error
3. For unknown KumaScript, generate a different error

The Compat API will not support KumaScript.
"""

from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type

from parsimonious.nodes import Node

from webplatformcompat.models import Specification
from .html import html_grammar, HTMLInterval, HTMLText, HTMLVisitor

kumascript_grammar = html_grammar + r"""
#
# KumaScript tokens
#
kumascript = ks_esc_start ks_name ks_arglist? ks_esc_end
ks_esc_start = "{{" _
ks_name = ~r"(?P<content>[^\(\}\s]*)\s*"s
ks_arglist = ks_func_start ks_arg ks_arg_rest* ks_func_end
ks_func_start = "(" _
ks_func_arg = _ "," _
ks_func_end = _ ")" _
ks_esc_end = "}}" _
ks_arg = (double_quoted_text / single_quoted_text / ks_bare_arg)
ks_bare_arg = ~r"(?P<content>.*?(?=[,)]))"
ks_arg_rest = ks_func_arg ks_arg

#
# Add KumaScript to text
#
text_token = kumascript / text_item
text_item = ~r"(?P<content>[^{<]+)"s
"""


@python_2_unicode_compatible
class KumaScript(HTMLText):
    """A KumaScript macro."""

    def __init__(self, raw_content, start, name, args, scope=None):
        super(KumaScript, self).__init__(raw_content, start)
        self.name = name
        self.args = args
        self.scope = scope

    def __str__(self):
        args = []
        for arg in self.args:
            if '"' in arg:
                quote = "'"
            else:
                quote = '"'
            args.append("{0}{1}{0}".format(quote, arg))
        if args:
            argtext = '(' + ', '.join(args) + ')'
        else:
            argtext = ''
        return "{{{{{}{}}}}}".format(self.name, argtext)

    def to_html(self):
        """Convert to HTML.  Default is an empty string."""
        return ''

    @property
    def known(self):
        return False

    def _make_issue(self, issue_slug):
        assert self.scope
        return (
            issue_slug, self.start, self.end,
            {'name': self.name, 'args': self.args, 'scope': self.scope,
             'kumascript': str(self)})

    @property
    def issues(self):
        return super(KumaScript, self).issues + [
            self._make_issue('unknown_kumascript')]


class KnownKumaScript(KumaScript):
    @property
    def known(self):
        return True

    @property
    def issues(self):
        return super(KumaScript, self).issues


class CompatAndroid(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatAndroid
    pass


class CompatGeckoDesktop(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoDesktop
    pass


class CompatGeckoFxOS(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoFxOS
    pass


class CompatGeckoMobile(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoMobile
    pass


class CompatNo(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatNo
    pass


class CompatUnknown(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatUnknown
    pass


class CompatVersionUnknown(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatVersionUnknown
    pass


class CompatibilityTable(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatibilityTable
    pass


class HTMLElement(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:HTMLElement
    pass


class Spec2(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:Spec2

    def __init__(self, *args, **kwargs):
        super(Spec2, self).__init__(*args, **kwargs)
        self.spec2_issues = []
        self.spec = None
        self.maturity = None
        key = self.mdn_key
        if key:
            try:
                self.spec = Specification.objects.get(mdn_key=key)
            except Specification.DoesNotExist:
                self.spec2_issues.append(
                    ('unknown_spec', self.start, self.end, {'key': key}))
            else:
                self.maturity = self.spec.maturity
        else:
            self.spec2_issues.append(self._make_issue('spec2_arg_count'))

    @property
    def mdn_key(self):
        try:
            return self.args[0]
        except IndexError:
            return None

    @property
    def issues(self):
        return super(Spec2, self).issues + self.spec2_issues


class SpecName(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:SpecName

    def __init__(self, *args, **kwargs):
        super(SpecName, self).__init__(*args, **kwargs)
        self.specname_issues = []
        self.spec = None
        key = self.mdn_key
        if key:
            try:
                self.spec = Specification.objects.get(mdn_key=key)
            except Specification.DoesNotExist:
                self.specname_issues.append(
                    ('unknown_spec', self.start, self.end, {'key': key}))
        else:
            self.specname_issues.append(self._make_issue('specname_blank_key'))

    @property
    def mdn_key(self):
        return self.args[0]

    @property
    def subpath(self):
        try:
            return self.args[1]
        except IndexError:
            return None

    @property
    def section_name(self):
        try:
            return self.args[2]
        except IndexError:
            return None

    @property
    def issues(self):
        return super(SpecName, self).issues + self.specname_issues


class CSSBox(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:cssbox
    pass


class CSSxRef(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:cssxref
    pass


class DeprecatedInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:deprecated_inline
    pass


class DOMxRef(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:domxref
    pass


class ExperimentalInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:experimental_inline
    pass


class NonStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:non-standard_inline
    pass


class NotStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:not_standard_inline
    pass


class PropertyPrefix(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:property_prefix
    pass


class XrefCSSLength(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csslength
    pass


class KumaVisitor(HTMLVisitor):
    """Extract HTML structure from a MDN Kuma raw fragment.

    Extracts KumaScript, with special handling if it is known.
    """

    def __init__(self, *args, **kwargs):
        super(KumaVisitor, self).__init__(*args, **kwargs)
        self._kumascript_proper_names = None
        self.scope = None

    def _visit_multi_block(self, node, tokens):
        """Visit a 1-or-more block of tokens."""
        assert isinstance(tokens, list)
        assert tokens
        if isinstance(tokens[0], list):
            # Unroll doubled list
            assert len(tokens) == 1
            tokens = tokens[0]
        for token in tokens:
            assert isinstance(token, HTMLInterval)
        return tokens

    def _visit_multi_token(self, node, children):
        """Visit a single HTMLInterval or list of HTMLIntervals."""
        assert len(children) == 1
        item = children[0]
        if isinstance(item, HTMLInterval):
            return item
        else:
            for subitem in item:
                assert isinstance(subitem, HTMLInterval), subitem
            if len(item) == 1:
                return item[0]
            else:
                return item

    visit_html_block = _visit_multi_block
    visit_html_tag = _visit_multi_token

    known_kumascript = {
        'CompatAndroid': CompatAndroid,
        'CompatGeckoDesktop': CompatGeckoDesktop,
        'CompatGeckoFxOS': CompatGeckoFxOS,
        'CompatGeckoMobile': CompatGeckoMobile,
        'CompatNo': CompatNo,
        'CompatUnknown': CompatUnknown,
        'CompatVersionUnknown': CompatVersionUnknown,
        'CompatibilityTable': CompatibilityTable,
        'HTMLElement': HTMLElement,
        'Spec2': Spec2,
        'SpecName': SpecName,
        'cssbox': CSSBox,
        'cssxref': CSSxRef,
        'deprecated_inline': DeprecatedInline,
        'domxref': DOMxRef,
        'experimental_inline': ExperimentalInline,
        'non-standard_inline': NonStandardInline,
        'not_standard_inline': NotStandardInline,
        'property_prefix': PropertyPrefix,
        'xref_csslength': XrefCSSLength,
    }

    def _kumascript_lookup(self, name):
        """
        Get the proper name and class for a KumaScript name.

        MDN does case-insensitive matching of KumaScript names.
        """
        if self._kumascript_proper_names is None:
            self._kumascript_proper_names = {}
            for k in self.known_kumascript.keys():
                self._kumascript_proper_names[k.lower()] = k
        proper_name = self._kumascript_proper_names.get(name.lower())
        if proper_name:
            return proper_name, self.known_kumascript[proper_name]
        else:
            return name, KumaScript

    def visit_kumascript(self, node, children):
        """Process a KumaScript macro."""
        esc0, name, arglist, esc1 = children
        assert isinstance(name, text_type), type(name)
        if isinstance(arglist, Node):
            assert arglist.start == arglist.end
            args = []
        else:
            assert isinstance(arglist, list), type(arglist)
            assert len(arglist) == 1
            args = arglist[0]
        assert isinstance(args, list), type(args)
        if args == ['']:
            args = []

        proper_name, ks_cls = self._kumascript_lookup(name)
        return self.process(ks_cls, node, proper_name, args, self.scope)

    visit_ks_name = HTMLVisitor._visit_content

    def visit_ks_arglist(self, node, children):
        f0, arg0, argrest, f1 = children
        args = [arg0]
        if isinstance(argrest, Node):
            # No additional args
            assert argrest.start == argrest.end
        else:
            for _, arg in argrest:
                args.append(arg)

        # Force to strings
        arglist = []
        for arg in args:
            if arg is None:
                arglist.append('')
            else:
                arglist.append(text_type(arg))
        return arglist

    def visit_ks_arg(self, node, children):
        assert isinstance(children, list)
        assert len(children) == 1
        item = children[0]
        assert isinstance(item, text_type)
        return item or None

    visit_ks_bare_arg = HTMLVisitor._visit_content

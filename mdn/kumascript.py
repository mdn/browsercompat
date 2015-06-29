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
from __future__ import unicode_literals

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
    def __init__(self, args=None, scope=None, **kwargs):
        """Initialize components of a KumaScript macro."""
        super(KumaScript, self).__init__(**kwargs)
        self.args = args or []
        self.scope = scope or '(unknown scope)'

    def arg(self, pos):
        """Return argument, or None if not enough arguments."""
        try:
            return self.args[pos]
        except IndexError:
            return None

    def __str__(self):
        """Create the programmer debug string."""
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
        name = getattr(self, 'name', 'KumaScript')
        return "{{{{{}{}}}}}".format(name, argtext)

    def to_html(self):
        """Convert to HTML.  Default is an empty string."""
        return ''

    def _make_issue(self, issue_slug, extra_kwargs=None):
        """Create an importer issue with standard KumaScript parameters."""
        assert self.scope
        kwargs = {'name': self.name, 'args': self.args, 'scope': self.scope,
                  'kumascript': str(self)}
        kwargs.update(extra_kwargs or {})
        return (issue_slug, self.start, self.end, kwargs)


class UnknownKumaScript(KumaScript):
    """An unknown KumaScript macro."""

    def __init__(self, name, **kwargs):
        """Initialize name of an unknown KumaScript macro."""
        super(UnknownKumaScript, self).__init__(**kwargs)
        self.name = name

    @property
    def known(self):
        return False

    @property
    def issues(self):
        """Return the list of issues with this KumaScript in this scope."""
        return super(UnknownKumaScript, self).issues + [
            self._make_issue('unknown_kumascript')]


class KnownKumaScript(KumaScript):
    """Base class for known KumaScript macros."""
    min_args = 0
    max_args = 0
    arg_names = []

    def __init__(self, args=None, scope=None, **kwargs):
        """Validate arg count of a known KumaScript macro."""
        super(KnownKumaScript, self).__init__(**kwargs)
        self.args = args or []
        self.scope = scope or '(unknown scope)'
        assert self.max_args >= self.min_args
        assert len(self.arg_names) == self.max_args

    @property
    def known(self):
        return True

    @property
    def name(self):
        return getattr(self, 'canonical_name', self.__class__.__name__)

    def _validate(self):
        """Return validation issues or empty list."""
        issues = []
        count = len(self.args)
        if count < self.min_args or count > self.max_args:
            extra = {
                'max': self.max_args, 'min': self.min_args, 'count': count,
                'arg_names': self.arg_names}
            if self.max_args == 0:
                arg_spec = "no arguments"
            else:
                if self.max_args == self.min_args:
                    arg_range = "exactly {0} argument{1}".format(
                        self.max_args, '' if self.max_args == 1 else 's')
                else:
                    arg_range = "between {0} and {1} arguments".format(
                        self.min_args, self.max_args)
                names = []
                for pos, name in enumerate(self.arg_names):
                    if pos > self.min_args:
                        names.append("[{}]".format(name))
                    else:
                        names.append(name)
                arg_spec = "{} ({})".format(arg_range, ', '.join(names))
            extra['arg_spec'] = arg_spec
            if count == 1:
                extra['arg_count'] = '1 argument'
            else:
                extra['arg_count'] = '{0} arguments'.format(count)

            issues.append(self._make_issue('kumascript_wrong_args', extra))
        return issues

    @property
    def issues(self):
        return super(KumaScript, self).issues + self._validate()


class CompatKumaScript(KnownKumaScript):
    """Base class for KumaScript specifying a browser version."""
    min_args = max_args = 1

    def to_html(self):
        return self.version


class CompatAndroid(CompatKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatAndroid
    arg_names = ['AndroidVersion']

    def __init__(self, **kwargs):
        super(CompatAndroid, self).__init__(**kwargs)
        self.version = self.arg(0)


class CompatGeckoDesktop(CompatKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoDesktop
    arg_names = ['GeckoVersion']
    geckoversion_to_version = {
        '1': '1.0',
        '1.0': '1.0',
        '1.7 or earlier': '1.0',
        '1.7': '1.0',
        '1.8': '1.5',
        '1.8.1': '2.0',
        '1.9': '3.0',
        '1.9.1': '3.5',
        '1.9.1.4': '3.5.4',
        '1.9.2': '3.6',
        '1.9.2.4': '3.6.4',
        '1.9.2.5': '3.6.5',
        '1.9.2.9': '3.6.9',
        '2': '4.0',
        '2.0': '4.0',
    }

    def __init__(self, **kwargs):
        super(CompatGeckoDesktop, self).__init__(**kwargs)
        self.gecko_version = self.arg(0)

    @property
    def version(self):
        try:
            return self.geckoversion_to_version[self.gecko_version]
        except KeyError:
            try:
                nversion = float(self.gecko_version)
            except ValueError:
                return None

            if nversion >= 5:
                return "{:1.1f}".format(nversion)
            else:
                return None

    @property
    def issues(self):
        issues = super(CompatGeckoDesktop, self).issues
        if self.version is None:
            issues.append(
                ('compatgeckodesktop_unknown', self.start, self.end,
                 {'version': self.gecko_version}))
        return issues


class CompatGeckoFxOS(CompatKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoFxOS
    max_args = 2
    arg_names = ['GeckoVersion', 'VersionOverride']

    def __init__(self, **kwargs):
        super(CompatGeckoFxOS, self).__init__(**kwargs)
        self.gecko_version = self.arg(0)
        over = self.arg(1)
        self.override = self.arg(1)

        # TODO: Replace with KumaScript logic
        try:
            nversion = float(self.gecko_version)
        except ValueError:
            nversion = -1
        over = self.override
        self.bad_version = False
        self.bad_override = False

        if (0 <= nversion < 19) and over in (None, '1.0'):
            self.version = '1.0'
        elif (0 <= nversion < 21) and over == '1.0.1':
            self.version = '1.0.1'
        elif (0 <= nversion < 24) and over in ('1.1', '1.1.0', '1.1.1'):
            self.version = '1.1'
        elif (19 <= nversion < 27) and over in (None, '1.2'):
            self.version = '1.2'
        elif (27 <= nversion < 29) and over in (None, '1.3'):
            self.version = '1.3'
        elif (29 <= nversion < 31) and over in (None, '1.4'):
            self.version = '1.4'
        elif (31 <= nversion < 33) and over in (None, '2.0'):
            self.version = '2.0'
        elif (33 <= nversion < 35) and over in (None, '2.1'):
            self.version = '2.1'
        elif (35 <= nversion < 38) and over in (None, '2.2'):
            self.version = '2.2'
        elif (nversion < 0 or nversion >= 38):
            self.version = over
            self.bad_version = True
        else:
            self.version = over
            self.bad_override = True
            self.version = over

    @property
    def issues(self):
        issues = super(CompatGeckoFxOS, self).issues
        if self.bad_version:
            issues.append(
                ('compatgeckofxos_unknown', self.start, self.end,
                 {'version': self.gecko_version}))
        if self.bad_override:
            issues.append(
                ('compatgeckofxos_override', self.start, self.end,
                 {'override': self.override, 'version': self.gecko_version}))
        return issues


class CompatGeckoMobile(CompatKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatGeckoMobile
    arg_names = ['GeckoVersion']

    def __init__(self, **kwargs):
        super(CompatGeckoMobile, self).__init__(**kwargs)
        self.gecko_version = self.arg(0)

    @property
    def version(self):
        nversion = self.gecko_version.split('.', 1)[0]
        if nversion == '2':
            return '4.0'
        else:
            return "{}.0".format(nversion)


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
    min_args = max_args = 1
    arg_names = ['ElementName']

    def __init__(self, **kwargs):
        super(HTMLElement, self).__init__(**kwargs)
        self.element_name = self.arg(0)

    def to_html(self):
        if ' ' in self.element_name:
            fmt = '<code>{}</code>'
        else:
            fmt = '<code>&lt;{}&gt;</code>'
        return fmt.format(self.element_name)


class SpecKumaScript(KnownKumaScript):
    """Base class for Spec2 and SpecName."""

    def __init__(self, **kwargs):
        super(SpecKumaScript, self).__init__(**kwargs)
        self.mdn_key = self.arg(0)
        self.spec = None
        if self.mdn_key:
            try:
                self.spec = Specification.objects.get(mdn_key=self.mdn_key)
            except Specification.DoesNotExist:
                pass

    def to_html(self):
        if self.spec:
            name = self.spec.name['en']
        else:
            name = self.mdn_key or "(None)"
        return "specification {}".format(name)


class Spec2(SpecKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:Spec2
    min_args = max_args = 1
    arg_names = ['SpecKey']

    def _validate(self):
        issues = super(Spec2, self)._validate()
        if self.scope == 'specification description':
            issues.append(self._make_issue('specdesc_spec2_invalid'))
        elif self.mdn_key and not self.spec:
            issues.append(
                ('unknown_spec', self.start, self.end, {'key': self.mdn_key}))
        return issues


class SpecName(SpecKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:SpecName
    min_args = 1
    max_args = 3
    arg_names = ['SpecKey', 'Anchor', 'AnchorName']

    def __init__(self, **kwargs):
        super(SpecName, self).__init__(**kwargs)
        self.subpath = self.arg(1)
        self.section_name = self.arg(2)

    def _validate(self):
        issues = super(SpecName, self)._validate()
        if self.mdn_key and not self.spec:
            issues.append(
                ('unknown_spec', self.start, self.end, {'key': self.mdn_key}))
        if not self.mdn_key and len(self.args):
            issues.append(self._make_issue('specname_blank_key'))
        return issues


class CSSBox(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:cssbox
    min_args = max_args = 1
    arg_names = ['PropertyName']
    canonical_name = 'cssbox'


class CSSxRef(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:cssxref
    min_args = 1
    max_args = 3
    arg_names = ['APIName', 'DisplayName', 'Anchor']
    canonical_name = 'cssxref'

    def __init__(self, **kwargs):
        super(CSSxRef, self).__init__(**kwargs)
        self.api_name = self.arg(0)
        self.display_name = self.arg(1)

    def to_html(self):
        return '<code>{}</code>'.format(self.display_name or self.api_name)


class DeprecatedInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:deprecated_inline
    canonical_name = 'deprecated_inline'


class DOMxRef(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:domxref
    min_args = 1
    max_args = 2
    arg_names = ['DOMPath', 'DOMText']
    canonical_name = 'domxref'

    def __init__(self, **kwargs):
        super(DOMxRef, self).__init__(**kwargs)
        self.dom_path = self.arg(0)
        self.dom_text = self.arg(1)

    def to_html(self):
        return '<code>{}</code>'.format(self.dom_text or self.dom_path)


class ExperimentalInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:experimental_inline
    canonical_name = 'experimental_inline'


class NonStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:non-standard_inline
    canonical_name = 'non-standard_inline'


class NotStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:not_standard_inline
    canonical_name = 'not_standard_inline'


class PropertyPrefix(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:property_prefix
    min_args = max_args = 1
    arg_names = ['Prefix']
    canonical_name = 'property_prefix'

    def __init__(self, **kwargs):
        super(PropertyPrefix, self).__init__(**kwargs)
        self.prefix = self.arg(0)


class XrefCSSLength(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csslength
    canonical_name = 'xref_csslength'

    def to_html(self):
        return '<code>&lt;length&gt;</code>'


class KumaVisitor(HTMLVisitor):
    """Extract HTML structure from a MDN Kuma raw fragment.

    Extracts KumaScript, with special handling if it is known.
    """

    def __init__(self, **kwargs):
        super(KumaVisitor, self).__init__(**kwargs)
        self._kumascript_proper_names = None
        self.scope = None

    def _visit_multi_block(self, node, children):
        """Visit a 1-or-more block of tokens."""
        assert children
        tokens = self.flatten(children)
        assert tokens
        for token in tokens:
            assert isinstance(token, HTMLInterval)
        return tokens

    def flatten(self, nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(self.flatten(item))
            else:
                result.append(item)
        return result

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
    visit_text_block = _visit_multi_block
    visit_text_token = _visit_multi_token

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
        return self.known_kumascript.get(proper_name)

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

        ks_cls = self._kumascript_lookup(name)
        if ks_cls:
            return self.process(ks_cls, node, args=args, scope=self.scope)
        else:
            return self.process(
                UnknownKumaScript, node, name=name, args=args,
                scope=self.scope)

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

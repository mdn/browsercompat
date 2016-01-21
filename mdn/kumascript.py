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
from django.utils.text import get_text_list

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node

from .data import Data
from .html import HTMLInterval, HTMLText, HTMLVisitor, html_grammar_source
from .utils import format_version

kumascript_grammar_source = html_grammar_source + r"""
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
# WhyNoSpec block
whynospec = _ whynospec_start whynospec_content whynospec_end
whynospec_start = ks_esc_start ~r"WhyNoSpecStart"s _ ks_esc_end _
whynospec_content = ~r".*?(?={{\s*WhyNoSpecEnd)"s
whynospec_end = ks_esc_start ~r"WhyNoSpecEnd"s _ ks_esc_end _

#
# Add KumaScript to text
#
text_token = whynospec / kumascript / text_item
text_item = ~r"(?P<content>(?:[^{<]|{(?!{))+)"s
"""
kumascript_grammar = Grammar(kumascript_grammar_source)

SCOPES = set((
    'specification name',
    'specification maturity',
    'specification description',
    'compatibility feature',
    'compatibility support',
    'footnote',
))

MDN_DOMAIN = 'https://developer.mozilla.org'
MDN_DOCS = MDN_DOMAIN + '/en-US/docs'


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
            args.append('{0}{1}{0}'.format(quote, arg))
        if args:
            argtext = '(' + ', '.join(args) + ')'
        else:
            argtext = ''
        name = getattr(self, 'name', 'KumaScript')
        return '{{{{{}{}}}}}'.format(name, argtext)

    def to_html(self):
        """Convert to HTML.  Default is an empty string."""
        return ''

    def _make_issue(self, issue_slug, **extra_kwargs):
        """Create an importer issue with standard KumaScript parameters."""
        assert self.scope
        kwargs = {'name': self.name, 'args': self.args, 'scope': self.scope,
                  'kumascript': str(self)}
        kwargs.update(extra_kwargs)
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
    expected_scopes = SCOPES

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
                arg_spec = 'no arguments'
            else:
                if self.max_args == self.min_args:
                    arg_range = 'exactly {0} argument{1}'.format(
                        self.max_args, '' if self.max_args == 1 else 's')
                else:
                    arg_range = 'between {0} and {1} arguments'.format(
                        self.min_args, self.max_args)
                names = []
                for pos, name in enumerate(self.arg_names):
                    if pos > self.min_args:
                        names.append('[{}]'.format(name))
                    else:
                        names.append(name)
                arg_spec = '{} ({})'.format(arg_range, ', '.join(names))
            extra['arg_spec'] = arg_spec
            if count == 1:
                extra['arg_count'] = '1 argument'
            else:
                extra['arg_count'] = '{0} arguments'.format(count)

            issues.append(self._make_issue('kumascript_wrong_args', **extra))
        assert not (self.expected_scopes - SCOPES)
        if self.scope not in self.expected_scopes:
            expected = get_text_list(sorted(self.expected_scopes))
            issues.append(self._make_issue(
                'unexpected_kumascript', expected_scopes=expected))
        return issues

    @property
    def issues(self):
        return super(KumaScript, self).issues + self._validate()


class Bug(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:Bug
    min_args = max_args = 1
    arg_names = ['number']
    canonical_name = 'bug'
    expected_scopes = set(('footnote',))

    def __init__(self, **kwargs):
        """
        Initialize Bug.

        {{bug}} macro takes 3 arguments, but only the 1-argument version is
        supported.
        """
        super(Bug, self).__init__(**kwargs)
        self.number = self.arg(0)

    def to_html(self):
        return (
            '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id={number}">'
            'bug {number}</a>').format(number=self.number)


class CompatKumaScript(KnownKumaScript):
    """Base class for KumaScript specifying a browser version."""

    min_args = max_args = 1
    expected_scopes = set(('compatibility support', ))

    def to_html(self):
        return self.version


class CompatBasicKumaScript(CompatKumaScript):
    """Base class for KumaScript specifying the actual browser version."""

    def __init__(self, **kwargs):
        super(CompatBasicKumaScript, self).__init__(**kwargs)
        self.version = format_version(self.arg(0))


class CompatAndroid(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatAndroid
    arg_names = ['AndroidVersion']


class CompatChrome(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatChrome
    arg_names = ['ChromeVer']


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
                return '{:1.1f}'.format(nversion)
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
            return '{}.0'.format(nversion)


class CompatIE(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatIE
    arg_names = ['IEver']


class CompatNightly(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatNightly
    max_args = 1
    arg_names = ['browser']
    expected_scopes = set(('compatibility support',))


class CompatNo(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatNo
    expected_scopes = set(('compatibility support',))


class CompatOpera(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatOpera
    arg_names = ['OperaVer']


class CompatOperaMobile(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatOperaMobile
    arg_names = ['OperaVer']


class CompatSafari(CompatBasicKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatSafari
    arg_names = ['SafariVer']


class CompatUnknown(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatUnknown
    expected_scopes = set(('compatibility support',))


class CompatVersionUnknown(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatVersionUnknown
    expected_scopes = set(('compatibility support',))


class CompatibilityTable(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:CompatibilityTable
    expected_scopes = set()


class KumaHTMLElement(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:HTMLElement
    min_args = max_args = 1
    arg_names = ['ElementName']
    canonical_name = 'HTMLElement'
    expected_scopes = set((
        'compatibility feature', 'compatibility support', 'footnote',
        'specification description'))

    def __init__(self, **kwargs):
        super(KumaHTMLElement, self).__init__(**kwargs)
        self.element_name = self.arg(0)

    def to_html(self):
        if ' ' in self.element_name:
            fmt = '<code>{}</code>'
        else:
            fmt = '<code>&lt;{}&gt;</code>'
        return fmt.format(self.element_name)


class SpecKumaScript(KnownKumaScript):
    """Base class for Spec2 and SpecName."""

    def __init__(self, data=None, **kwargs):
        super(SpecKumaScript, self).__init__(**kwargs)
        self.mdn_key = self.arg(0)
        self.spec = None
        self.data = data or Data()
        if self.mdn_key:
            self.spec = self.data.lookup_specification(self.mdn_key)

    def to_html(self):
        if self.spec:
            name = self.spec.name['en']
        else:
            name = self.mdn_key or '(None)'
        return 'specification {}'.format(name)


class Spec2(SpecKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:Spec2
    min_args = max_args = 1
    arg_names = ['SpecKey']
    expected_scopes = set(('specification maturity',))

    def _validate(self):
        issues = super(Spec2, self)._validate()
        if self.mdn_key and not self.spec:
            issues.append(
                ('unknown_spec', self.start, self.end, {'key': self.mdn_key}))
        return issues


class SpecName(SpecKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:SpecName
    min_args = 1
    max_args = 3
    arg_names = ['SpecKey', 'Anchor', 'AnchorName']
    expected_scopes = set(('specification name', 'specification description'))

    def __init__(self, **kwargs):
        super(SpecName, self).__init__(**kwargs)
        self.subpath = self.arg(1)
        self.section_name = self.arg(2)
        if self.spec:
            self.section_id = self.data.lookup_section_id(
                self.spec.id, self.subpath)
        else:
            self.section_id = None

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
    expected_scopes = set()


class XRefBase(KnownKumaScript):
    """Base class for cross-reference KumaScript."""

    expected_scopes = set((
        'compatibility feature', 'specification description', 'footnote'))

    def __init__(self, **kwargs):
        super(XRefBase, self).__init__(**kwargs)
        self.url = None
        self.display = None
        self.linked = self.scope in ('specification description', 'footnote')

    def to_html(self):
        """Convert macro to link or plain text."""
        assert self.display
        if self.linked:
            assert self.url
            return '<a href="{}"><code>{}</code></a>'.format(
                self.url, self.display)
        else:
            return '<code>{}</code>'.format(self.display)


class CSSxRef(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:cssxref
    min_args = 1
    max_args = 3
    arg_names = ['APIName', 'DisplayName', 'Anchor']
    canonical_name = 'cssxref'

    def __init__(self, **kwargs):
        super(CSSxRef, self).__init__(**kwargs)
        self.api_name = self.arg(0)
        self.display_name = self.arg(1)
        self.anchor = self.arg(2)
        self.construct_crossref(
            self.api_name, self.display_name, self.anchor)

    def construct_crossref(self, api_name, display_name, anchor=None):
        self.url = '{}/Web/CSS/{}{}'.format(
            MDN_DOCS, api_name, anchor or '')
        self.display = display_name or api_name


class DeprecatedInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:deprecated_inline
    canonical_name = 'deprecated_inline'
    expected_scopes = set(('compatibility feature',))


class DOMEventXRef(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:domeventxref
    min_args = max_args = 1
    arg_names = ['api_name']
    canonical_name = 'domeventxref'

    def __init__(self, **kwargs):
        """Initialize DOMEventXRef.

        Only implements the subset of domeventxref used on current pages.
        """
        super(DOMEventXRef, self).__init__(**kwargs)
        self.api_name = self.arg(0)
        assert '()' not in self.api_name
        self.url = '{}/DOM/DOM_event_reference/{}'.format(
            MDN_DOCS, self.api_name)
        self.display = self.api_name


class DOMException(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:exception
    min_args = max_args = 1
    arg_names = ['exception_id']
    canonical_name = 'exception'

    def __init__(self, **kwargs):
        super(DOMException, self).__init__(**kwargs)
        self.exception_id = self.arg(0)
        self.url = '{}/Web/API/DOMException#{}'.format(
            MDN_DOCS, self.exception_id)
        self.display = self.exception_id


class DOMxRef(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:domxref
    min_args = 1
    max_args = 2
    arg_names = ['DOMPath', 'DOMText']
    canonical_name = 'domxref'

    def __init__(self, **kwargs):
        super(DOMxRef, self).__init__(**kwargs)
        self.dom_path = self.arg(0)
        self.dom_text = self.arg(1)
        path = self.dom_path.replace(' ', '_').replace('()', '')
        if '.' in path and '..' not in path:
            path = path.replace('.', '/')
        path = path[0].upper() + path[1:]
        self.url = '{}/Web/API/{}'.format(MDN_DOCS, path)
        self.display = self.dom_text or self.dom_path


class EmbedCompatTable(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:EmbedCompatTable
    min_args = max_args = 1
    arg_names = ['slug']
    expected_scopes = set(('footnote',))


class Event(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:event
    min_args = 1
    max_args = 2
    arg_names = ['api_name', 'display_name']
    canonical_name = 'event'

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.api_name = self.arg(0)
        self.display_name = self.arg(1)
        self.url = '{}/Web/Events/{}'.format(MDN_DOCS, self.api_name)
        self.display = self.display_name or self.api_name


class ExperimentalInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:experimental_inline
    canonical_name = 'experimental_inline'
    expected_scopes = set(('compatibility feature',))


class GeckoRelease(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:geckoRelease
    min_args = max_args = 1
    arg_names = ['release']
    canonical_name = 'geckoRelease'
    expected_scopes = set(('footnote',))
    early_versions = {
        '1.8': ('Firefox 1.5', 'Thunderbird 1.5', 'SeaMonkey 1.0'),
        '1.8.1': ('Firefox 2', 'Thunderbird 2', 'SeaMonkey 1.1'),
        '1.9': ('Firefox 3',),
        '1.9.1': ('Firefox 3.5', 'Thunderbird 3.0', 'SeaMonkey 2.0'),
        '1.9.1.4': ('Firefox 3.5.4',),
        '1.9.2': ('Firefox 3.6', 'Thunderbird 3.1', 'Fennec 1.0'),
        '1.9.2.4': ('Firefox 3.6.4',),
        '1.9.2.5': ('Firefox 3.6.5',),
        '1.9.2.9': ('Firefox 3.6.9',),
        '2.0b2': ('Firefox 4.0b2',),
        '2.0b4': ('Firefox 4.0b4',),
        '2': ('Firefox 4', 'Thunderbird 3.3', 'SeaMonkey 2.1'),
        '2.0': ('Firefox 4', 'Thunderbird 3.3', 'SeaMonkey 2.1'),
        '2.1': ('Firefox 4 Mobile',),
    }
    firefoxos_name = 'Firefox OS {}'
    firefoxos_versions = {
        '18.0': ('1.0.1', '1.1'),
        '26.0': ('1.2',),
        '28.0': ('1.3',),
        '30.0': ('1.4',),
        '32.0': ('2.0',),
    }
    release_names = (
        'Firefox {rnum}', 'Thunderbird {rnum}', 'SeaMonkey 2.{snum}')

    def __init__(self, **kwargs):
        super(GeckoRelease, self).__init__(**kwargs)
        raw_version = self.arg(0)
        self.gecko_version = raw_version
        self.and_higher = False
        if raw_version.endswith('+'):
            self.gecko_version = raw_version[:-1]
            self.and_higher = True

        if self.gecko_version in self.early_versions:
            self.releases = self.early_versions[self.gecko_version]
        else:
            vnum = float(self.gecko_version)
            assert vnum >= 5.0
            rnum = '{:.1f}'.format(vnum)
            snum = int(vnum) - 3
            self.releases = [
                name.format(rnum=rnum, snum=snum)
                for name in self.release_names]
            for fxosnum in self.firefoxos_versions.get(rnum, []):
                self.releases.append(self.firefoxos_name.format(fxosnum))

    def to_html(self):
        plus = '+' if self.and_higher else ''
        return '(' + ' / '.join([rel + plus for rel in self.releases]) + ')'


class HTMLAttrXRef(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:htmlattrxref
    min_args = 1
    max_args = 2
    arg_names = ['attribute', 'element']
    canonical_name = 'htmlattrxref'

    def __init__(self, **kwargs):
        super(HTMLAttrXRef, self).__init__(**kwargs)
        self.attribute = self.arg(0)
        self.element = self.arg(1)
        self.text = self.arg(2)
        if self.element:
            self.url = '{}/Web/HTML/Element/{}'.format(MDN_DOCS, self.element)
        else:
            self.url = '{}/Web/HTML/Global_attributes'.format(MDN_DOCS)
        self.url += '#attr-' + self.attribute.lower()
        self.display = self.attribute.lower()


class JSxRef(XRefBase):
    # https://developer.mozilla.org/en-US/docs/Template:jsxref
    min_args = 1
    max_args = 2
    arg_names = ['API name', 'display name']
    canonical_name = 'jsxref'

    def __init__(self, **kwargs):
        """
        Initialize JSxRef.

        {{jsxref}} macro can take 4 arguments, but only handling first two.
        """
        super(JSxRef, self).__init__(**kwargs)
        self.api_name = self.arg(0)
        self.display_name = self.arg(1)
        path_name = self.api_name.replace('.prototype.', '/').replace('()', '')
        if path_name.startswith('Global_Objects/'):
            path_name = path_name.replace('Global_Objects/', '', 1)
        if '.' in path_name and '...' not in path_name:
            path_name = path_name.replace('.', '/')
        self.url = '{}/Web/JavaScript/Reference/Global_Objects/{}'.format(
            MDN_DOCS, path_name)
        self.display = self.display_name or self.api_name


class NonStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:non-standard_inline
    canonical_name = 'non-standard_inline'
    expected_scopes = set(('compatibility feature',))


class NotStandardInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:not_standard_inline
    canonical_name = 'not_standard_inline'
    expected_scopes = set(('compatibility feature',))


class ObsoleteInline(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:obsolete_inline
    canonical_name = 'obsolete_inline'
    expected_scopes = set(('compatibility feature',))


class PropertyPrefix(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:property_prefix
    min_args = max_args = 1
    arg_names = ['Prefix']
    canonical_name = 'property_prefix'
    expected_scopes = set(('compatibility support',))

    def __init__(self, **kwargs):
        super(PropertyPrefix, self).__init__(**kwargs)
        self.prefix = self.arg(0)


class WebkitBug(KnownKumaScript):
    # https://developer.mozilla.org/en-US/docs/Template:WebkitBug
    min_args = max_args = 1
    arg_names = ['number']
    expected_scopes = set(('footnote',))

    def __init__(self, **kwargs):
        super(WebkitBug, self).__init__(**kwargs)
        self.number = self.arg(0)

    def to_html(self):
        return (
            '<a href="https://bugs.webkit.org/show_bug.cgi?id={number}">'
            'WebKit bug {number}</a>').format(number=self.number)


class WhyNoSpecBlock(HTMLInterval):
    """Psuedo-element for {{WhyNoSpecStart}}/{{WhyNoSpecEnd}} block.

    Stand-alone {{WhyNoSpecStart}} and {{WhyNoSpecEnd}} elements will be
    treated as unknown kumascript.

    https://developer.mozilla.org/en-US/docs/Template:WhyNoSpecStart
    https://developer.mozilla.org/en-US/docs/Template:WhyNoSpecEnd
    """

    expected_scopes = set()

    def __init__(self, scope=None, **kwargs):
        super(WhyNoSpecBlock, self).__init__(**kwargs)
        self.scope = scope

    def to_html(self, drop_tag=None):
        return ''


class XrefCSSBase(CSSxRef):
    """Base class for xref_cssXXX macros."""

    min_args = max_args = 0
    arg_names = []

    def __init__(self, **kwargs):
        super(XrefCSSBase, self).__init__(**kwargs)
        self.construct_crossref(*self.xref_args)


class XrefCSSAngle(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssangle
    canonical_name = 'xref_cssangle'
    xref_args = ('angle', '&lt;angle&gt;')


class XrefCSSColorValue(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csscolorvalue
    canonical_name = 'xref_csscolorvalue'
    xref_args = ('color_value', '&lt;color&gt;')


class XrefCSSGradient(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssgradient
    canonical_name = 'xref_cssgradient'
    xref_args = ('gradient', '&lt;gradient&gt;')


class XrefCSSImage(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssimage
    canonical_name = 'xref_cssimage'
    xref_args = ('image', '&lt;image&gt;')


class XrefCSSInteger(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssinteger
    canonical_name = 'xref_cssinteger'
    xref_args = ('integer', '&lt;integer&gt;')


class XrefCSSLength(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csslength
    canonical_name = 'xref_csslength'
    xref_args = ('length', '&lt;length&gt;')


class XrefCSSNumber(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssnumber
    canonical_name = 'xref_cssnumber'
    xref_args = ('number', '&lt;number&gt;')


class XrefCSSPercentage(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_csspercentage
    canonical_name = 'xref_csspercentage'
    xref_args = ('percentage', '&lt;percentage&gt;')


class XrefCSSString(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssstring
    canonical_name = 'xref_cssstring'
    xref_args = ('string', '&lt;string&gt;')


class XrefCSSVisual(XrefCSSBase):
    # https://developer.mozilla.org/en-US/docs/Template:xref_cssvisual
    canonical_name = 'xref_cssvisual'
    xref_args = ('Media/Visual', '&lt;visual&gt;')


class BaseKumaVisitor(HTMLVisitor):
    """Extract HTML structure from a MDN Kuma raw fragment.

    Extracts KumaScript, with special handling if it is known.
    """

    scope = None

    def __init__(self, **kwargs):
        super(BaseKumaVisitor, self).__init__(**kwargs)
        self._kumascript_proper_names = None

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
    visit_html_element = _visit_multi_token
    visit_text_block = _visit_multi_block
    visit_text_token = _visit_multi_token

    known_kumascript = {
        'Bug': Bug,
        'CompatAndroid': CompatAndroid,
        'CompatChrome': CompatChrome,
        'CompatGeckoDesktop': CompatGeckoDesktop,
        'CompatGeckoFxOS': CompatGeckoFxOS,
        'CompatGeckoMobile': CompatGeckoMobile,
        'CompatIE': CompatIE,
        'CompatNightly': CompatNightly,
        'CompatNo': CompatNo,
        'CompatOpera': CompatOpera,
        'CompatOperaMobile': CompatOperaMobile,
        'CompatSafari': CompatSafari,
        'CompatUnknown': CompatUnknown,
        'CompatVersionUnknown': CompatVersionUnknown,
        'CompatibilityTable': CompatibilityTable,
        'EmbedCompatTable': EmbedCompatTable,
        'HTMLElement': KumaHTMLElement,
        'Spec2': Spec2,
        'SpecName': SpecName,
        'WebkitBug': WebkitBug,
        'cssbox': CSSBox,
        'cssxref': CSSxRef,
        'deprecated_inline': DeprecatedInline,
        'domeventxref': DOMEventXRef,
        'domxref': DOMxRef,
        'event': Event,
        'exception': DOMException,
        'experimental_inline': ExperimentalInline,
        'geckoRelease': GeckoRelease,
        'htmlattrxref': HTMLAttrXRef,
        'jsxref': JSxRef,
        'non-standard_inline': NonStandardInline,
        'not_standard_inline': NotStandardInline,
        'obsolete_inline': ObsoleteInline,
        'property_prefix': PropertyPrefix,
        'xref_cssangle': XrefCSSAngle,
        'xref_csscolorvalue': XrefCSSColorValue,
        'xref_cssgradient': XrefCSSGradient,
        'xref_cssimage': XrefCSSImage,
        'xref_cssinteger': XrefCSSInteger,
        'xref_csslength': XrefCSSLength,
        'xref_cssnumber': XrefCSSNumber,
        'xref_csspercentage': XrefCSSPercentage,
        'xref_cssstring': XrefCSSString,
        'xref_cssvisual': XrefCSSVisual,
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
        init_args = {'args': args, 'scope': self.scope}
        if ks_cls is None:
            ks_cls = UnknownKumaScript
            init_args['name'] = name
        if issubclass(ks_cls, SpecKumaScript):
            init_args['data'] = self.data
        return self.process(ks_cls, node, **init_args)

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

    def visit_whynospec(self, node, children):
        return self.process(WhyNoSpecBlock, node, scope=self.scope)


class KumaVisitor(BaseKumaVisitor):
    """Extract HTML structure from a MDN Kuma raw fragment.

    Include extra policy for scraping pages for the importer:
    - Converts <span>content</span> to "content", with issues
    - Validate and cleanup <a> tags
    - Keeps <div id="foo">, for detecting compat divs
    - Keeps <td colspan=# rowspan=#>, for detecting spanning compat cells
    - Keeps <th colspan=#>, for detecting spanning compat headers
    - Keeps <h2 id="id" name="name">, for warning on mismatch
    - Raises issues on all other attributes
    """

    _default_attribute_actions = {None: 'ban'}

    def visit_a_open(self, node, children):
        """Validate and cleanup <a> open tags."""
        actions = self._default_attribute_actions.copy()
        actions['href'] = 'must'
        actions['title'] = 'drop'
        actions['class'] = 'keep'
        converted = self._visit_open(node, children, actions)

        # Convert relative links to absolute links
        attrs = converted.attributes.attrs
        if 'href' in attrs:
            href = attrs['href'].value
            if href and href[0] == '/':
                attrs['href'].value = MDN_DOMAIN + href

        # Drop class attribute, warning if unexpected
        if 'class' in attrs:
            class_attr = attrs.pop('class')
            for value in class_attr.value.split():
                if value in ('external', 'external-icon'):
                    pass
                else:
                    self.add_issue(
                        'unexpected_attribute', class_attr, node_type='a',
                        ident='class', value=value,
                        expected='the attribute href')

        return converted

    def visit_div_open(self, node, children):
        """Retain id attribute of <div> tags."""
        actions = self._default_attribute_actions.copy()
        actions['id'] = 'keep'
        return self._visit_open(node, children, actions)

    def visit_td_open(self, node, children):
        """Retain colspan and rowspan attributes of <td> tags."""
        actions = self._default_attribute_actions.copy()
        actions['colspan'] = 'keep'
        actions['rowspan'] = 'keep'
        return self._visit_open(node, children, actions)

    def visit_th_open(self, node, children):
        """Retain colspan attribute of <th> tags."""
        actions = self._default_attribute_actions.copy()
        actions['colspan'] = 'keep'
        return self._visit_open(node, children, actions)

    def _visit_hn_open(self, node, children, actions=None, **kwargs):
        """Retain id and name attributes of <h#> tags."""
        actions = self._default_attribute_actions.copy()
        actions['id'] = 'keep'
        actions['name'] = 'keep'
        return self._visit_open(node, children, actions, **kwargs)

    visit_h1_open = _visit_hn_open
    visit_h2_open = _visit_hn_open
    visit_h3_open = _visit_hn_open
    visit_h4_open = _visit_hn_open
    visit_h5_open = _visit_hn_open
    visit_h6_open = _visit_hn_open

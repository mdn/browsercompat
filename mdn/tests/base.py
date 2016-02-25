# coding: utf-8
"""Define base TestCase for MDN tests."""
from webplatformcompat.tests.base import TestCase as BaseTestCase
from webplatformcompat.models import (
    Browser, Feature, Maturity, Reference, Section, Specification, Version)


class TestCase(BaseTestCase):
    """TestCase that provides get_instance for loading specification data."""

    longMessage = True  # On assertions, print values and message
    _instance_specs = {
        ('Maturity', 'CR'): {'name': '{"en": "Candidate Recommendation"}'},
        ('Maturity', 'WD'): {'name': '{"en": "Working Draft"}'},
        ('Maturity', 'Standard'): {'name': '{"en": "Standard"}'},
        ('Maturity', 'Living Standard'): {'name': '{"en": "Living Standard"}'},
        ('Specification', 'css3_backgrounds'): {
            '_req': {'maturity': ('Maturity', 'CR')},
            'mdn_key': 'CSS3 Backgrounds',
            'name': (
                '{"en": "CSS Backgrounds and Borders Module Level&nbsp;3"}'),
            'uri': '{"en": "http://dev.w3.org/csswg/css3-background/"}'},
        ('Specification', 'css3_display'): {
            '_req': {'maturity': ('Maturity', 'WD')},
            'mdn_key': 'CSS3 Display',
            'name': '{"en" : "CSS Display Module Level 3"}',
            'uri': '{"en" : "http://dev.w3.org/csswg/css-display/"}'},
        ('Specification', 'css3_ui'): {
            '_req': {'maturity': ('Maturity', 'WD')},
            'mdn_key': 'CSS3 UI',
            'name': '{"en": "CSS Basic User Interface Module Level&nbsp;3"}',
            'uri': '{"en": "http://dev.w3.org/csswg/css3-ui/"}'},
        ('Specification', 'web_audio_api'): {
            '_req': {'maturity': ('Maturity', 'WD')},
            'mdn_key': 'Web Audio API',
            'name': '{"en": "Web Audio API"}',
            'uri': '{"en": "http://webaudio.github.io/web-audio-api/"}'},
        ('Specification', 'es1'): {
            '_req': {'maturity': ('Maturity', 'Standard')},
            'mdn_key': 'ES1',
            'name': '{"en": "ECMAScript 1st Edition (ECMA-262)"}',
            'uri': ('{"en": "http://www.ecma-international.org/publications/'
                    'files/ECMA-ST-ARCH/ECMA-262,%201st%20edition,'
                    '%20June%201997.pdf"}')},
        ('Specification', 'html_whatwg'): {
            '_req': {'maturity': ('Maturity', 'Living Standard')},
            'mdn_key': 'HTML WHATWG',
            'name': '{"en": "WHATWG HTML Living Standard"}',
            'uri': '{"en": "https://html.spec.whatwg.org/multipage/"}'},
        ('Section', 'background-size'): {
            '_req': {'specification': ('Specification', 'css3_backgrounds')},
            'subpath': '{"en": "#the-background-size"}'},
        ('Reference', ('web-css-background-size', 'background-size')): {},
        ('Feature', 'web'): {'name': '{"en": "Web"}'},
        ('Feature', 'web-css'): {
            '_req': {'parent': ('Feature', 'web')}, 'name': '{"en": "CSS"}'},
        ('Feature', 'web-css-background-size'): {
            '_req': {'parent': ('Feature', 'web-css')},
            'name': '{"zxx": "background-size"}'},
        ('Feature', 'web-css-background-size-contain_and_cover'): {
            '_req': {'parent': ('Feature', 'web-css-background-size')},
            'name': '{"en": "<code>contain</code> and <code>cover</code>"}'},
        ('Browser', 'chrome_desktop'): {
            'name': '{"en": "Chrome for Desktop"}'},
        ('Browser', 'firefox_desktop'): {
            'name': '{"en": "Firefox for Desktop"}'},
        ('Version', ('chrome_desktop', '1.0')): {},
        ('Version', ('firefox_desktop', 'current')): {},
        ('Version', ('firefox_desktop', '1.0')): {},
    }

    name_to_class = {
        'Browser': Browser,
        'Feature': Feature,
        'Maturity': Maturity,
        'Reference': Reference,
        'Section': Section,
        'Specification': Specification,
        'Version': Version,
    }

    def get_instance(self, model_cls_name, slug):
        """Get a test fixture instance, creating on first access."""
        instance_key = (model_cls_name, slug)
        if not hasattr(self, '_instances'):
            self._instances = {}
        if instance_key not in self._instances:
            attrs = self._instance_specs[instance_key].copy()

            # Load implied and explicit required instances
            req = attrs.pop('_req', {})
            if model_cls_name == 'Version':
                browser_slug, version = slug
                attrs['browser'] = self.get_instance('Browser', browser_slug)
                attrs['version'] = version
            elif model_cls_name == 'Section':
                attrs['name'] = '{"en": "%s"}' % slug
            elif model_cls_name == 'Reference':
                feature_slug, section_slug = slug
                attrs['feature'] = self.get_instance('Feature', feature_slug)
                attrs['section'] = self.get_instance('Section', section_slug)
            else:
                attrs['slug'] = slug
            for req_name, (req_type, req_slug) in req.items():
                attrs[req_name] = self.get_instance(req_type, req_slug)

            # Create the instance
            model_cls = self.name_to_class[model_cls_name]
            self._instances[instance_key] = self.create(model_cls, **attrs)
        return self._instances[instance_key]

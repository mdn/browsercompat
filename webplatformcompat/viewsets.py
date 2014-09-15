# -*- coding: utf-8 -*-

try:  # pragma: no cover
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    # py26 doesn't have OrderedDict
    OrderedDict = dict
assert OrderedDict

from django.contrib.auth.models import User
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet as BaseModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet as BaseROModelViewSet
from rest_framework.viewsets import ViewSet

from .mixins import PartialPutMixin
from .models import Browser, BrowserVersion
from .parsers import JsonApiParser
from .renderers import JsonApiRenderer
from .serializers import (
    BrowserSerializer, BrowserVersionSerializer,
    HistoricalBrowserSerializer, HistoricalBrowserVersionSerializer,
    UserSerializer)


#
# Base classes
#

class ModelViewSet(PartialPutMixin, BaseModelViewSet):
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)
    parser_classes = (JsonApiParser, FormParser, MultiPartParser)


class ReadOnlyModelViewSet(BaseROModelViewSet):
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)


#
# 'Regular' viewsets
#

class BrowserViewSet(ModelViewSet):
    model = Browser
    serializer_class = BrowserSerializer
    filter_fields = ('slug',)


class BrowserVersionViewSet(ModelViewSet):
    model = BrowserVersion
    serializer_class = BrowserVersionSerializer
    filter_fields = ('browser', 'browser__slug', 'version', 'status')


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    filter_fields = ('username',)


#
# Historical object viewsets
#

class HistoricalBrowserViewSet(ReadOnlyModelViewSet):
    model = Browser.history.model
    serializer_class = HistoricalBrowserSerializer
    filter_fields = ('id', 'slug')


class HistoricalBrowserVersionViewSet(ReadOnlyModelViewSet):
    model = BrowserVersion.history.model
    serializer_class = HistoricalBrowserVersionSerializer
    filter_fields = ('id',)


#
# Views
#

class ViewFeaturesViewSet(ViewSet):
    '''Return a view for FeatureSets

    TODO: Return real data
    '''
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)
    permission_classes = (AllowAny,)

    def get_renderer_context(self):
        context = super(ViewFeaturesViewSet, self).get_renderer_context()
        context['jsonapi'] = {'direct': True}
        return context

    def list(self, request, *args, **kwargs):
        url = reverse(
            'viewfeatures-detail', request=request,
            kwargs={'pk': 'html-element-address'})
        feature_sets = {
            'view-features': OrderedDict((
                ('html-element-address', url),
            ))
        }
        return Response(feature_sets)

    def retrieve(self, request, *args, **kwargs):
        feature_set = OrderedDict((
            ("features", OrderedDict((
                ("id", "816"),
                ("slug", "html-element-address"),
                ("maturity", "standard"),
                ("mdn-path", "en-US/docs/Web/HTML/Element/address"),
                ("name", "address"),
                ("links", OrderedDict((
                    ("specification-sections", ["746", "421", "70"]),
                    ("browser-version-features", []),
                    ("parent", "800"),
                    ("ancestors", ["800", "816"]),
                    ("siblings", ["814", "815", "816", "817", "818"]),
                    ("children", ["191"]),
                    ("descendants", ["816", "191"]),
                    ("history-current", "216"),
                    ("history", ["216"])))),
            ))),
            ("linked", OrderedDict((
                ("features", [
                    OrderedDict((
                        ("id", "191"),
                        ("slug", "html-address"),
                        ("maturity", "standard"),
                        ("name", {"en": "Basic support"}),
                        ("links", OrderedDict((
                            ("specification-sections", []),
                            ("browser-version-features", [
                                "358", "359", "360", "361", "362", "363",
                                "364", "365", "366", "367", "368"]),
                            ("parent", "816"),
                            ("ancestors", ["800", "816", "191"]),
                            ("siblings", ["191"]),
                            ("children", []),
                            ("descendants", ["191"]),
                            ("history-current", "395"),
                            ("history", ["395"]),
                        ))),
                    )),
                ]),
                ("specification-sections", [
                    OrderedDict((
                        ("id", "746"),
                        ("name", {"en": "The address element"}),
                        ("subpath",
                         {"en": "sections.html#the-address-element"}),
                        ("notes", None),
                        ("links", OrderedDict((
                            ("specification", "273"),
                            ("features", []),
                            ("features", ["816"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "421"),
                        ("name", {"en": "The address element"}),
                        ("subpath",
                         {"en": "sections.html#the-address-element"}),
                        ("notes", None),
                        ("links", OrderedDict((
                            ("specification", "114"),
                            ("features", ["816"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "70"),
                        ("name", {"en": "The ADDRESS element"}),
                        ("subpath", {"en": "struct/global.html#h-7.5.6"}),
                        ("notes", None),
                        ("links", OrderedDict((
                            ("specification", "576"),
                            ("features", ["816"]),
                        ))),
                    )),
                ]),
                ("specifications", [
                    OrderedDict((
                        ("id", "62"),
                        ("kumu-key", "HTML WHATWG"),
                        ("name", {"en": "WHATWG HTML Living Standard"}),
                        ("uri", {
                            "en": (
                                "http://www.whatwg.org/specs/web-apps/"
                                "current-work/multipage/"),
                        }),
                        ("links", OrderedDict((
                            ("specification-sections", ["745", "746", "747"]),
                            ("specification-status", "23"),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "114"),
                        ("kumu-key", "HTML5 W3C"),
                        ("name", {"en": "HTML5"}),
                        ("uri", {"en": "http://www.w3.org/TR/html5/"}),
                        ("links", OrderedDict((
                            ("specification-sections", ["420", "421", "422"]),
                            ("specification-status", "52"),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "576"),
                        ("kumu-key", "HTML4.01"),
                        ("name", {"en": "HTML 4.01 Specification"}),
                        ("uri", {"en": "http://www.w3.org/TR/html401/"}),
                        ("links", OrderedDict((
                            ("specification-sections", ["69", "70", "71"]),
                            ("specification-status", "49"),
                        ))),
                    )),
                ]),
                ("specification-statuses", [
                    OrderedDict((
                        ("id", "23"),
                        ("mdn-key", "Living"),
                        ("name", {"en": "Living Standard"}),
                        ("links", {"specifications": ["62"]}),
                    )),
                    OrderedDict((
                        ("id", "49"),
                        ("mdn-key", "REC"),
                        ("name", OrderedDict((
                            ("en", "Recommendation"),
                            ("jp", "勧告"),
                        ))),
                        ("links", {
                            "specifications": [
                                "84", "85", "272", "273", "274", "576"]
                        }),
                    )),
                    OrderedDict((
                        ("id", "52"),
                        ("mdn-key", "CR"),
                        ("name", OrderedDict((
                            ("en", "Candidate Recommendation"),
                            ("ja", "勧告候補"),
                        ))),
                        ("links", {
                            "specifications": ["83", "113", "114", "115"],
                        }),
                    )),
                ]),
                ("browser-version-features", [
                    OrderedDict((
                        ("id", "358"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "758"),
                            ("feature", "191"),
                            ("history-current", "3567"),
                            ("history", ["3567"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "359"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "759"),
                            ("feature", "191"),
                            ("history-current", "3568"),
                            ("history", ["3568"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "360"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "760"),
                            ("feature", "191"),
                            ("history-current", "3569"),
                            ("history", ["3569"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "361"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "761"),
                            ("feature", "191"),
                            ("history-current", "3570"),
                            ("history", ["3570"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "362"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "762"),
                            ("feature", "191"),
                            ("history-current", "3571"),
                            ("history", ["3571"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "362"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "762"),
                            ("feature", "191"),
                            ("history-current", "3571"),
                            ("history", ["3571"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "362"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "762"),
                            ("feature", "191"),
                            ("history-current", "3571"),
                            ("history", ["3571"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "363"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "763"),
                            ("feature", "191"),
                            ("history-current", "3572"),
                            ("history", ["3572"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "364"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "764"),
                            ("feature", "191"),
                            ("history-current", "3573"),
                            ("history", ["3573"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "365"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "765"),
                            ("feature", "191"),
                            ("history-current", "3574"),
                            ("history", ["3574"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "366"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "766"),
                            ("feature", "191"),
                            ("history-current", "3575"),
                            ("history", ["3575"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "367"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "767"),
                            ("feature", "191"),
                            ("history-current", "3576"),
                            ("history", ["3576"]),
                        ))),
                    )),
                    OrderedDict((
                        ("id", "368"),
                        ("support", "yes"),
                        ("prefix", None),
                        ("note", None),
                        ("footnote", None),
                        ("links", OrderedDict((
                            ("browser-version", "768"),
                            ("feature", "191"),
                            ("history-current", "3577"),
                            ("history", ["3577"]),
                        ))),
                    )),
                ]),
                ("browser-versions", [
                    OrderedDict((
                        ("id", "758"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "1"),
                            ("browser-version-features",
                             ["158", "258", "358", "458"]),
                            ("history-current", "1567"),
                            ("history", ["1567"]),
                        ))),
                    )), OrderedDict((
                        ("id", "759"),
                        ("version", "1.0"),
                        ("release-day", "2004-12-09"),
                        ("retirement-day", "2005-02-24"),
                        ("status", "retired"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "2"),
                            ("browser-version-features",
                             ["159", "259", "359", "459"]),
                            ("history-current", "1568"),
                            ("history", ["1568"]),
                        ))),
                    )), OrderedDict((
                        ("id", "760"),
                        ("version", "1.0"),
                        ("release-day", "1995-08-16"),
                        ("retirement-day", None),
                        ("status", "retired"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "3"),
                            ("browser-version-features",
                             ["160", "260", "360", "460"]),
                            ("history-current", "1569"),
                            ("history", ["1569"]),
                        ))),
                    )), OrderedDict((
                        ("id", "761"),
                        ("version", "5.12"),
                        ("release-day", "2001-06-27"),
                        ("retirement-day", None),
                        ("status", "retired"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "4"),
                            ("browser-version-features",
                             ["161", "261", "361", "461"]),
                            ("history-current", "1570"),
                            ("history", ["1570"]),
                        ))),
                    )), OrderedDict((
                        ("id", "762"),
                        ("version", "1.0"),
                        ("release-day", "2003-06-23"),
                        ("retirement-day", None),
                        ("status", "retired"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "5"),
                            ("browser-version-features",
                             ["162", "262", "362", "462"]),
                            ("history-current", "1571"),
                            ("history", ["1571"]),
                        ))),
                    )), OrderedDict((
                        ("id", "763"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "6"),
                            ("browser-version-features",
                             ["163", "263", "363", "463"]),
                            ("history-current", "1572"),
                            ("history", ["1572"]),
                        ))),
                    )), OrderedDict((
                        ("id", "764"),
                        ("version", "1.0"),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "retired"),
                        ("release-notes-uri", None),
                        ("note", "Uses Gecko 1.7"),
                        ("links", OrderedDict((
                            ("browser", "7"),
                            ("browser-version-features",
                             ["164", "264", "364", "464"]),
                            ("history-current", "1574"),
                            ("history", ["1574"]),
                        ))),
                    )), OrderedDict((
                        ("id", "765"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "8"),
                            ("browser-version-features",
                             ["165", "265", "365", "465"]),
                            ("history-current", "1575"),
                            ("history", ["1575"]),
                        ))),
                    )), OrderedDict((
                        ("id", "766"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "11"),
                            ("browser-version-features",
                             ["166", "266", "366", "466"]),
                            ("history-current", "1576"),
                            ("history", ["1576"]),
                        ))),
                    )), OrderedDict((
                        ("id", "767"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "9"),
                            ("browser-version-features",
                             ["167", "267", "367", "467"]),
                            ("history-current", "1577"),
                            ("history", ["1577"]),
                        ))),
                    )), OrderedDict((
                        ("id", "768"),
                        ("version", None),
                        ("release-day", None),
                        ("retirement-day", None),
                        ("status", "current"),
                        ("release-notes-uri", None),
                        ("note", None),
                        ("links", OrderedDict((
                            ("browser", "10"),
                            ("browser-version-features",
                             ["168", "268", "368", "468"]),
                            ("history-current", "1578"),
                            ("history", ["1578"]),
                        ))),
                    )),
                ]),
                ("browsers", [
                    OrderedDict((
                        ("id", "1"),
                        ("slug", "chrome"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/chrome.png")),
                        ("name", OrderedDict((
                            ("en", "Chrome"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["123", "758"]),
                            ("history-current", "1001"),
                            ("history", ["1001"]),
                        ))),
                    )), OrderedDict((
                        ("id", "2"),
                        ("slug", "firefox"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/firefox.png")),
                        ("name", OrderedDict((
                            ("en", "Firefox"),
                        ))),
                        ("note", OrderedDict((
                            ("en", "Uses Gecko for its web browser engine."),
                        ))),
                        ("links", OrderedDict((
                            ("versions", ["124", "759"]),
                            ("history-current", "1002"),
                            ("history", ["1002"]),
                        ))),
                    )), OrderedDict((
                        ("id", "3"),
                        ("slug", "ie"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/ie.png")),
                        ("name", OrderedDict((
                            ("en", "Internet Explorer"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["125", "167", "178", "760"]),
                            ("history-current", "1003"),
                            ("history", ["1003"]),
                        ))),
                    )), OrderedDict((
                        ("id", "4"),
                        ("slug", "opera"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/opera.png")),
                        ("name", OrderedDict((
                            ("en", "Opera"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["126", "761"]),
                            ("history-current", "1004"),
                            ("history", ["1004"]),
                        ))),
                    )), OrderedDict((
                        ("id", "5"),
                        ("slug", "safari"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/safari.png")),
                        ("name", OrderedDict((
                            ("en", "Safari"),
                        ))),
                        ("note", OrderedDict((
                            ("en", "Uses Webkit for its web browser engine."),
                        ))),
                        ("links", OrderedDict((
                            ("versions", ["127", "762"]),
                            ("history-current", "1005"),
                            ("history", ["1005"]),
                        ))),
                    )), OrderedDict((
                        ("id", "6"),
                        ("slug", "android"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/android.png")),
                        ("name", OrderedDict((
                            ("en", "Android"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["128", "763"]),
                            ("history-current", "1006"),
                            ("history", ["1006"]),
                        ))),
                    )), OrderedDict((
                        ("id", "7"),
                        ("slug", "firefox-mobile"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/firefox-mobile.png")),
                        ("name", OrderedDict((
                            ("en", "Firefox Mobile"),
                        ))),
                        ("note", OrderedDict((
                            ("en", "Uses Gecko for its web browser engine."),
                        ))),
                        ("links", OrderedDict((
                            ("versions", ["129", "764"]),
                            ("history-current", "1007"),
                            ("history", ["1007"]),
                        ))),
                    )), OrderedDict((
                        ("id", "8"),
                        ("slug", "ie-phone"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/ie-phone.png")),
                        ("name", OrderedDict((
                            ("en", "IE Phone"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["130", "765"]),
                            ("history-current", "1008"),
                            ("history", ["1008"]),
                        ))),
                    )), OrderedDict((
                        ("id", "9"),
                        ("slug", "opera-mobile"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/opera-mobile.png")),
                        ("name", OrderedDict((
                            ("en", "Opera Mobile"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["131", "767"]),
                            ("history-current", "1009"),
                            ("history", ["1009"]),
                        ))),
                    )), OrderedDict((
                        ("id", "10"),
                        ("slug", "safari-mobile"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/safari-mobile.png")),
                        ("name", OrderedDict((
                            ("en", "Safari Mobile"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["132", "768"]),
                            ("history-current", "1010"),
                            ("history", ["1010"]),
                        ))),
                    )), OrderedDict((
                        ("id", "11"),
                        ("slug", "opera-mini"),
                        ("icon", (
                            "https://compat.cdn.mozilla.net/media/img/"
                            "browsers/opera-mini.png")),
                        ("name", OrderedDict((
                            ("en", "Opera Mini"),
                        ))),
                        ("note", None),
                        ("links", OrderedDict((
                            ("versions", ["131", "766"]),
                            ("history-current", "1019"),
                            ("history", ["1019"]),
                        ))),
                    )),
                ]),
            ))),
            ("links", OrderedDict((
                ("feature.features", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{feature.features}")),
                    ("type", "features"),
                ))),
                ("features.specification-sections", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "specification-sections/"
                        "{features.specification-sections}")),
                    ("type", "specfication-sections"),
                ))),
                ("features.parent", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{features.parent}")),
                    ("type", "features"),
                ))),
                ("features.ancestors", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{features.ancestors}")),
                    ("type", "features"),
                ))),
                ("features.siblings", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{features.siblings}")),
                    ("type", "features"),
                ))),
                ("features.children", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{features.children}")),
                    ("type", "features"),
                ))),
                ("features.descendants", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/features/"
                        "{features.descendants}")),
                    ("type", "features"),
                ))),
                ("features.history-current", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-features/"
                        "{features.history-current}")),
                    ("type", "historical-features"),
                ))),
                ("features.history", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-features/"
                        "{features.history}")),
                    ("type", "historical-features"),
                ))),
                ("browsers.versions", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/browser-versions/"
                        "{browsers.versions}")),
                    ("type", "browser-versions"),
                ))),
                ("browsers.history-current", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/historical-browsers/"
                        "{browsers.history-current}")),
                    ("type", "historical-browsers"),
                ))),
                ("browsers.history", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/historical-browsers/"
                        "{browsers.history}")),
                    ("type", "historical-browsers"),
                ))),
                ("browser-versions.browser", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/browsers/"
                        "{browser-versions.browser}")),
                    ("type", "browsers"),
                ))),
                ("browser-versions.browser-version-features", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "browser-version-features/"
                        "{browser-versions.features}")),
                    ("type", "browser-version-features"),
                ))),
                ("browser-versions.history-current", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-browser-versions/"
                        "{browser-versions.history-current}")),
                    ("type", "historical-browser-versions"),
                ))),
                ("browser-versions.history", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-browser-versions/"
                        "{browser-versions.history}")),
                    ("type", "historical-browser-versions"),
                ))),
                ("browser-version-features.browser-version", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/browser-versions/"
                        "{browser-version-features.browser-version}")),
                    ("type", "browser-versions"),
                ))),
                ("browser-version-features.feature", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/browsers/"
                        "{browser-version-features.feature}")),
                    ("type", "features"),
                ))),
                ("browser-version-features.history-current", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-browser-version-features/"
                        "{browser-version-features.history-current}")),
                    ("type", "historical-browser-version-features"),
                ))),
                ("browser-version-features.history", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "historical-browser-version-features/"
                        "{browser-version-features.history}")),
                    ("type", "historical-browser-version-features"),
                ))),
                ("specifications.specification-sections", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "specification-sections/"
                        "{specifications.specification-sections}")),
                    ("type", "specification-sections"),
                ))),
                ("specifications.specification-status", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "specification-statuses/"
                        "{specifications.specification-status}")),
                    ("type", "specification-statuses"),
                ))),
                ("specification-sections.specification", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/specifications/"
                        "{specification-sections.specification}")),
                    ("type", "specifications"),
                ))),
                ("specification-sections.features", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/"
                        "specification-sections/"
                        "{specification-sections.features}")),
                    ("type", "features"),
                ))),
                ("specification-statuses.specifications", OrderedDict((
                    ("href", (
                        "https://api.compat.mozilla.org/specifications/"
                        "{specification-statuses.specifications}")),
                    ("type", "specifications"),
                ))),
            ))),
            ("meta", OrderedDict((
                ("compat-table", OrderedDict((
                    ("tabs", [
                        OrderedDict((
                            ("name", OrderedDict((
                                ("en", "Desktop"),
                            ))),
                            ("browsers", ["1", "2", "3", "4", "5"]),
                        )),
                        OrderedDict((
                            ("name", OrderedDict((
                                ("en", "Mobile"),
                            ))),
                            ("browsers", ["6", "7", "8", "11", "9", "10"]),
                        )),
                    ]),
                    ("browser-version-features", OrderedDict((
                        ("191", OrderedDict((
                            ("1", ["358"]),
                            ("2", ["359"]),
                            ("3", ["360"]),
                            ("4", ["361"]),
                            ("5", ["362"]),
                            ("6", ["363"]),
                            ("7", ["364"]),
                            ("8", ["365"]),
                            ("11", ["366"]),
                            ("9", ["367"]),
                            ("10", ["368"]),
                        ))),
                    ))),
                ))),
            ))),
        ))
        return Response(feature_set)

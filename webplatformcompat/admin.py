from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Browser, Feature, Version


class BrowserAdmin(SimpleHistoryAdmin):
    pass


class VersionAdmin(SimpleHistoryAdmin):
    pass


class FeatureAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Browser, BrowserAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Feature, FeatureAdmin)

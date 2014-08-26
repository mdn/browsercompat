from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Browser, BrowserVersion


class BrowserAdmin(SimpleHistoryAdmin):
    pass


class BrowserVersionAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Browser, BrowserAdmin)
admin.site.register(BrowserVersion, BrowserVersionAdmin)

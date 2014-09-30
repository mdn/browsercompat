from django.views.generic import TemplateView


class RequestContextMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(RequestContextMixin, self).get_context_data(**kwargs)
        ctx['request'] = self.request
        return ctx


class RequestView(RequestContextMixin, TemplateView):
    pass

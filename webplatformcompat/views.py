from django.views.generic import TemplateView


class RequestContextMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(RequestContextMixin, self).get_context_data(**kwargs)
        ctx['request'] = self.request
        return ctx


class RequestView(RequestContextMixin, TemplateView):
    pass


class ViewFeature(RequestContextMixin, TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super(ViewFeature, self).get_context_data(**kwargs)
        ctx['feature_id'] = self.kwargs['feature_id']
        return ctx

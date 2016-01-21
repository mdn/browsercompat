"""Support (non-API) views."""
from django.views.generic import TemplateView


class ViewFeature(TemplateView):

    def get_context_data(self, **kwargs):
        ctx = super(ViewFeature, self).get_context_data(**kwargs)
        ctx['feature_id'] = kwargs['feature_id']
        return ctx

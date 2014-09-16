from rest_framework.utils.encoders import JSONEncoder
from rest_framework_json_api.renderers import JsonApiRenderer \
    as BaseJsonApiRender
from rest_framework_json_api.renderers import WrapperNotApplicable
from rest_framework_json_api.utils import snakecase


class JsonApiRenderer(BaseJsonApiRender):
    encoder_class = JSONEncoder
    wrappers = ['wrap_jsonapi_aware'] + BaseJsonApiRender.wrappers

    def wrap_jsonapi_aware(self, data, renderer_context):
        jsonapi = renderer_context.get('jsonapi', {})
        direct = jsonapi.get('direct')
        if not jsonapi or not direct:
            raise WrapperNotApplicable('No jsonapi in context')
        return data

    def model_to_resource_type(self, model):
        if model:
            return snakecase(model._meta.verbose_name_plural)
        else:
            return 'data'

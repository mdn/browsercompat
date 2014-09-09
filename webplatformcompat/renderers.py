from rest_framework.utils.encoders import JSONEncoder
from rest_framework_json_api.renderers import JsonApiRenderer \
    as BaseJsonApiRender
from rest_framework_json_api.utils import slug


class JsonApiRenderer(BaseJsonApiRender):
    encoder_class = JSONEncoder

    def model_to_resource_type(self, model):
        if model:
            return slug(model._meta.verbose_name_plural)
        else:
            return 'data'

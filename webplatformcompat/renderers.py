from rest_framework.utils.encoders import JSONEncoder
from rest_framework_json_api.renderers import JsonApiRenderer \
    as BaseJsonApiRender


class JsonApiRenderer(BaseJsonApiRender):
    encoder_class = JSONEncoder

# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet as BaseModelViewSet
from rest_framework_json_api.parsers import JsonApiParser

from .renderers import JsonApiRenderer
from .serializers import UserSerializer


class ModelViewSet(BaseModelViewSet):
    renderer_classes = (JsonApiRenderer, BrowsableAPIRenderer)
    parser_classes = (JsonApiParser, FormParser, MultiPartParser)


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer

# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer

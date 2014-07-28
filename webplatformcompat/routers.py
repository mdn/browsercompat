# -*- coding: utf-8 -*-

from rest_framework.routers import DefaultRouter

from .viewsets import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

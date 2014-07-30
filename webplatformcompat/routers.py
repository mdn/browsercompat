# -*- coding: utf-8 -*-

from rest_framework.routers import DefaultRouter

from .viewsets import BrowserViewSet, BrowserVersionViewSet, UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'browsers', BrowserViewSet)
router.register(r'browser-versions', BrowserVersionViewSet)
router.register(r'users', UserViewSet)

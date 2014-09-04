from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase as BaseAPITestCase


class APITestCase(BaseAPITestCase):
    '''APITestCase with useful methods'''
    maxDiff = None
    baseUrl = 'http://testserver'

    def reverse(self, viewname, **kwargs):
        '''Create a full URL for a view'''
        return self.baseUrl + reverse(viewname, kwargs=kwargs)

    def login_superuser(self):
        '''Create and login a superuser, saving to self.user'''
        user = User.objects.create(
            username='staff', is_staff=True, is_superuser=True)
        user.set_password('5T@FF')
        user.save()
        self.assertTrue(self.client.login(username='staff', password='5T@FF'))
        self.user = user
        return user

    def create(self, klass, _history_user=None, _history_date=None, **kwargs):
        '''Create a model, setting the historical relations'''
        obj = klass(**kwargs)
        obj._history_user = (
            _history_user or getattr(self, 'user', None) or
            self.login_superuser())
        if _history_date:
            obj._history_date = _history_date
        obj.save()
        return obj

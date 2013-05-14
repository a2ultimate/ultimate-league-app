# -*- coding: utf-8 -*-

from django.utils import translation
from django.db.models import ObjectDoesNotExist

from pybb.signals import user_saved


class PybbMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                # Here we try to load profile, but can get error
                # if user created during syncdb but profile model
                # under south control. (Like pybb.Profile).
                profile = request.user.get_profile()
            except ObjectDoesNotExist:
                # Ok, we should create new profile for this user
                # and grant permissions for add posts
                user_saved(request.user, created=True)
                profile = request.user.get_profile()

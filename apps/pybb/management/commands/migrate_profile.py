#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models

class Command(BaseCommand):
    args = ''
    help = 'Migrate pybb profiles to local site profile'

    def handle(self, *args, **options):
        profile_app, profile_model = settings.AUTH_PROFILE_MODULE.split('.')
        profile_model = ContentType.objects.get(app_label=profile_app, model=profile_model).model_class()
        for user in User.objects.all():
            #print(u'migrating profile for %s\n' % user.username)
            pybb_profile = user.pybb_profile
            try:
                profile = user.get_profile()
            except profile_model.DoesNotExist:
                profile = profile_model(user=user)
            profile.post_count = pybb_profile.post_count
            profile.save()
        self.stdout.write('All profiles successfuly migrated')

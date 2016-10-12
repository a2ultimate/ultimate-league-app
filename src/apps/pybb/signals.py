# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.conf import settings
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete

from pybb import defaults


def post_saved(instance, **kwargs):

    if kwargs['created']:
        profile = instance.user.profile
        profile.post_count = instance.user.posts.count()
        profile.save()

def post_deleted(instance, **kwargs):
    profile = instance.user.profile
    profile.post_count = instance.user.posts.count()
    profile.save()

def user_saved(instance, created, **kwargs):
    if not created:
        return
    try:
        add_post_permission = Permission.objects.get_by_natural_key('add_post', 'pybb', 'post')
        add_topic_permission = Permission.objects.get_by_natural_key('add_topic', 'pybb', 'topic')
    except ObjectDoesNotExist:
        return
    instance.user_permissions.add(add_post_permission, add_topic_permission)
    instance.save()
    # if settings.AUTH_PROFILE_MODULE == 'pybb.Profile':
    #     from models import Profile
    #     Profile(user=instance).save()

def setup_signals():
    from models import Post
    post_save.connect(post_saved, sender=Post)
    post_delete.connect(post_deleted, sender=Post)
    if defaults.PYBB_AUTO_USER_PERMISSIONS:
        post_save.connect(user_saved, sender=settings.AUTH_USER_MODEL)

# -*- coding: utf-8 -*-
import re
import inspect

from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

try:
    from django.utils.timezone import now as tznow
except ImportError:
    import datetime

    tznow = datetime.datetime.now

from pybb.models import Topic, Post, Profile
from pybb import defaults




class PostForm(forms.ModelForm):
    name = forms.CharField(label=_('Subject'))

    class Meta(object):
        model = Post
        fields = ('body',)

    def __init__(self, *args, **kwargs):
    #Move args to kwargs
        if args:
            kwargs.update(dict(zip(inspect.getargspec(super(PostForm, self).__init__)[0][1:], args)))
        self.user = kwargs.pop('user', None)
        self.ip = kwargs.pop('ip', None)
        self.topic = kwargs.pop('topic', None)
        self.forum = kwargs.pop('forum', None)
        if not (self.topic or self.forum or ('instance' in kwargs)):
            raise ValueError('You should provide topic, forum or instance')
        if ('instance' in kwargs) and kwargs['instance'] and (kwargs['instance'].topic.head == kwargs['instance']):
            kwargs.setdefault('initial', {})['name'] = kwargs['instance'].topic.name

        super(PostForm, self).__init__(**kwargs)

        # remove topic specific fields
        if not (self.forum or (self.instance.pk and (self.instance.topic.head == self.instance))):
            del self.fields['name']

    def clean_body(self):
        body = self.cleaned_data['body']
        user = self.user or self.instance.user
        if defaults.PYBB_BODY_VALIDATOR:
            defaults.PYBB_BODY_VALIDATOR(user, body)

        for cleaner in defaults.PYBB_BODY_CLEANERS:
            body = cleaner(user, body)
        return body

    def clean(self):
        return self.cleaned_data

    def save(self, commit=True):
        if self.instance.pk:
            post = super(PostForm, self).save(commit=False)
            if self.user:
                post.user = self.user
            if post.topic.head == post:
                post.topic.name = self.cleaned_data['name']
                post.topic.updated = tznow()
                if commit:
                    post.topic.save()
            if commit:
                post.save()
            return post

        allow_post = True
        if defaults.PYBB_PREMODERATION:
            allow_post = defaults.PYBB_PREMODERATION(self.user, self.cleaned_data['body'])
        if self.forum:
            topic = Topic(
                forum=self.forum,
                user=self.user,
                name=self.cleaned_data['name'],
            )
            if not allow_post:
                topic.on_moderation = True
            if commit:
                topic.save()
        else:
            topic = self.topic
        post = Post(topic=topic, user=self.user, user_ip=self.ip,
            body=self.cleaned_data['body'])
        if not allow_post:
            post.on_moderation = True
        if commit:
            post.save()
        return post


class AdminPostForm(PostForm):
    """
    Superusers can post messages from any user and from any time
    If no user with specified name - new user will be created
    """
    login = forms.CharField(label=_('User'))

    def __init__(self, *args, **kwargs):
        if args:
            kwargs.update(dict(zip(inspect.getargspec(forms.ModelForm.__init__)[0][1:], args)))
        if 'instance' in kwargs and kwargs['instance']:
            kwargs.setdefault('initial', {}).update({'login': kwargs['instance'].user.email})
        super(AdminPostForm, self).__init__(**kwargs)

    def save(self, *args, **kwargs):
        try:
            self.user = get_user_model().objects.filter(email=self.cleaned_data['login']).get()
        except get_user_model().DoesNotExist:
            self.user = get_user_model().objects.create_user(self.cleaned_data['login'],
                '%s@example.com' % self.cleaned_data['login'])
        return super(AdminPostForm, self).save(*args, **kwargs)

try:
    profile_app, profile_model = 'leauges.player'.split('.')
    profile_model = ContentType.objects.get_by_natural_key(profile_app, profile_model).model_class()
except (AttributeError, ValueError, ObjectDoesNotExist):
    profile_model = Profile




class UserSearchForm(forms.Form):
    query = forms.CharField(required=False, label='')

    def filter(self, qs):
        if self.is_valid():
            query = self.cleaned_data['query']
            return qs.filter(email__contains=query)
        else:
            return qs

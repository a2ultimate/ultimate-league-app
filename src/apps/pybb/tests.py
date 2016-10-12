# -*- coding: utf-8 -*-

import time, datetime


from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Permission
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

try:
    from lxml import html
except ImportError:
    raise Exception('PyBB requires lxml for self testing')

from pybb import defaults
from pybb.models import *

__author__ = 'zeus'


class SharedTestModule(object):

    def create_user(self):
        self.user = get_user_model().objects.create_user('zeus', 'zeus@localhost', 'zeus')

    def login_client(self, username='zeus', password='zeus'):
        self.client.login(username=username, password=password)

    def create_initial(self, post=True):
        self.category = Category(name='foo')
        self.category.save()
        self.forum = Forum(name='xfoo', description='bar', category=self.category)
        self.forum.save()
        self.topic = Topic(name='etopic', forum=self.forum, user=self.user)
        self.topic.save()
        if post:
            self.post = Post(topic=self.topic, user=self.user, body='bbcode [b]test[b]')
            self.post.save()

    def get_form_values(self, response, form="post-form"):
        return dict(html.fromstring(response.content).xpath('//form[@class="%s"]' % form)[0].form_values())


class FeaturesTest(TestCase, SharedTestModule):
    def setUp(self):
        self.ORIG_PYBB_ENABLE_ANONYMOUS_POST = defaults.PYBB_ENABLE_ANONYMOUS_POST
        self.ORIG_PYBB_PREMODERATION = defaults.PYBB_PREMODERATION
        defaults.PYBB_PREMODERATION = False
        defaults.PYBB_ENABLE_ANONYMOUS_POST = False
        self.create_user()
        self.create_initial()
        mail.outbox = []

    def test_base(self):
        # Check index page
        url = reverse('pybb:index')
        response = self.client.get(url)
        parser = html.HTMLParser(encoding='utf8')
        tree = html.fromstring(response.content, parser=parser)
        self.assertContains(response, u'foo')
        self.assertContains(response, self.forum.get_absolute_url())
        self.assertTrue(defaults.PYBB_DEFAULT_TITLE in tree.xpath('//title')[0].text_content())
        self.assertEqual(len(response.context['categories']), 1)

    def test_forum_page(self):
        # Check forum page
        response = self.client.get(self.forum.get_absolute_url())
        self.assertEqual(response.context['forum'], self.forum)
        tree = html.fromstring(response.content)
        self.assertTrue(tree.xpath('//a[@href="%s"]' % self.topic.get_absolute_url()))
        self.assertTrue(tree.xpath('//title[contains(text(),"%s")]' % self.forum.name))
        self.assertFalse(tree.xpath('//a[contains(@href,"?page=")]'))
        self.assertFalse(response.context['is_paginated'])

    def test_category_page(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.forum.get_absolute_url())

    def test_profile_edit(self):
        # Self profile edit
        self.login_client()
        response = self.client.get(reverse('pybb:edit_profile'))
        self.assertEqual(response.status_code, 200)
        values = self.get_form_values(response, 'profile-edit')
        response = self.client.post(reverse('pybb:edit_profile'), data=values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.get(self.post.get_absolute_url(), follow=True)
        response = self.client.post(reverse('pybb:edit_profile'), data=values, follow=True)
        self.assertEqual(len(response.context['form'].errors), 0)

    def test_pagination_and_topic_addition(self):
        for i in range(0, defaults.PYBB_FORUM_PAGE_SIZE + 3):
            topic = Topic(name='topic_%s_' % i, forum=self.forum, user=self.user)
            topic.save()
        url = reverse('pybb:forum', args=[self.forum.id])
        response = self.client.get(url)
        self.assertEqual(len(response.context['topic_list']), defaults.PYBB_FORUM_PAGE_SIZE)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['paginator'].num_pages,
                         ((defaults.PYBB_FORUM_PAGE_SIZE + 3) / defaults.PYBB_FORUM_PAGE_SIZE) + 1)

    def test_bbcode_and_topic_title(self):
        response = self.client.get(self.topic.get_absolute_url())
        tree = html.fromstring(response.content)
        self.assertTrue(self.topic.name in tree.xpath('//title')[0].text_content())
        self.assertContains(response, self.post.body_html)
        self.assertContains(response, u'bbcode <strong>test</strong>')

    def test_topic_addition(self):
        self.login_client()
        add_topic_url = reverse('pybb:add_topic', kwargs={'forum_id': self.forum.id})
        response = self.client.get(add_topic_url)
        values = self.get_form_values(response)
        values['body'] = 'new topic test'
        values['name'] = 'new topic name'
        response = self.client.post(add_topic_url, data=values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Topic.objects.filter(name='new topic name').exists())

    def test_post_deletion(self):
        post = Post(topic=self.topic, user=self.user, body='bbcode [b]test[b]')
        post.save()
        post.delete()
        Topic.objects.get(id=self.topic.id)
        Forum.objects.get(id=self.forum.id)

    def test_topic_deletion(self):
        topic = Topic(name='xtopic', forum=self.forum, user=self.user)
        topic.save()
        post = Post(topic=topic, user=self.user, body='one')
        post.save()
        post = Post(topic=topic, user=self.user, body='two')
        post.save()
        post.delete()
        Topic.objects.get(id=topic.id)
        Forum.objects.get(id=self.forum.id)
        topic.delete()
        Forum.objects.get(id=self.forum.id)

    def test_forum_updated(self):
        time.sleep(1)
        topic = Topic(name='xtopic', forum=self.forum, user=self.user)
        topic.save()
        post = Post(topic=topic, user=self.user, body='one')
        post.save()
        post = Post.objects.get(id=post.id)
        self.assertTrue(self.forum.updated==post.created)

    def test_latest_topics(self):
        topic_1 = self.topic
        topic_1.updated = datetime.datetime.utcnow()
        topic_2 = Topic.objects.create(name='topic_2', forum=self.forum, user=self.user)
        topic_2.updated = datetime.datetime.utcnow() + datetime.timedelta(days=-1)

        category_2 = Category.objects.create(name='cat2')
        forum_2 = Forum.objects.create(name='forum_2', category=category_2)
        topic_3 = Topic.objects.create(name='topic_3', forum=forum_2, user=self.user)
        topic_3.updated = datetime.datetime.utcnow() + datetime.timedelta(days=-2)

        self.login_client()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['topic_list']), [topic_1, topic_2, topic_3])

        topic_2.forum.hidden = True
        topic_2.forum.save()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_3])

        topic_2.forum.hidden = False
        topic_2.forum.save()
        category_2.hidden = True
        category_2.save()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_1, topic_2])

        topic_2.forum.hidden = False
        topic_2.forum.save()
        category_2.hidden = False
        category_2.save()
        topic_1.on_moderation = True
        topic_1.save()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_1, topic_2, topic_3])

        topic_1.user = get_user_model().objects.create_user('another', 'another@localhost', 'another')
        topic_1.save()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_2, topic_3])

        topic_1.forum.moderators.add(self.user)
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_1, topic_2, topic_3])

        topic_1.forum.moderators.remove(self.user)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_1, topic_2, topic_3])

        self.client.logout()
        response = self.client.get(reverse('pybb:topic_latest'))
        self.assertListEqual(list(response.context['topic_list']), [topic_2, topic_3])

    def test_hidden(self):
        client = Client()
        category = Category(name='hcat', hidden=True)
        category.save()
        forum_in_hidden = Forum(name='in_hidden', category=category)
        forum_in_hidden.save()
        topic_in_hidden = Topic(forum=forum_in_hidden, name='in_hidden', user=self.user)
        topic_in_hidden.save()

        forum_hidden = Forum(name='hidden', category=self.category, hidden=True)
        forum_hidden.save()
        topic_hidden = Topic(forum=forum_hidden, name='hidden', user=self.user)
        topic_hidden.save()

        post_hidden = Post(topic=topic_hidden, user=self.user, body='hidden')
        post_hidden.save()

        post_in_hidden = Post(topic=topic_in_hidden, user=self.user, body='hidden')
        post_in_hidden.save()


        self.assertFalse(category.id in [c.id for c in client.get(reverse('pybb:index')).context['categories']])
        self.assertEqual(client.get(category.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(forum_in_hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(topic_in_hidden.get_absolute_url()).status_code, 404)

        self.assertNotContains(client.get(reverse('pybb:index')), forum_hidden.get_absolute_url())
        self.assertNotContains(client.get(reverse('pybb:feed_topics')), topic_hidden.get_absolute_url())
        self.assertNotContains(client.get(reverse('pybb:feed_topics')), topic_in_hidden.get_absolute_url())

        self.assertNotContains(client.get(reverse('pybb:feed_posts')), post_hidden.get_absolute_url())
        self.assertNotContains(client.get(reverse('pybb:feed_posts')), post_in_hidden.get_absolute_url())
        self.assertEqual(client.get(forum_hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(topic_hidden.get_absolute_url()).status_code, 404)

        client.login(username='zeus', password='zeus')
        self.assertFalse(category.id in [c.id for c in client.get(reverse('pybb:index')).context['categories']])
        self.assertNotContains(client.get(reverse('pybb:index')), forum_hidden.get_absolute_url())
        self.assertEqual(client.get(category.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(forum_in_hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(topic_in_hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(forum_hidden.get_absolute_url()).status_code, 404)
        self.assertEqual(client.get(topic_hidden.get_absolute_url()).status_code, 404)
        self.user.is_staff = True
        self.user.save()
        self.assertTrue(category.id in [c.id for c in client.get(reverse('pybb:index')).context['categories']])
        self.assertContains(client.get(reverse('pybb:index')), forum_hidden.get_absolute_url())
        self.assertNotEqual(client.get(category.get_absolute_url()).status_code, 404)
        self.assertNotEqual(client.get(forum_in_hidden.get_absolute_url()).status_code, 404)
        self.assertNotEqual(client.get(topic_in_hidden.get_absolute_url()).status_code, 404)
        self.assertNotEqual(client.get(forum_hidden.get_absolute_url()).status_code, 404)
        self.assertNotEqual(client.get(topic_hidden.get_absolute_url()).status_code, 404)

    def test_inactive(self):
        self.login_client()
        url = reverse('pybb:add_post', kwargs={'topic_id': self.topic.id})
        response = self.client.get(url)
        values = self.get_form_values(response)
        values['body'] = 'test ban'
        response = self.client.post(url, values, follow=True)
        self.assertEqual(len(Post.objects.filter(body='test ban')), 1)
        self.user.is_active = False
        self.user.save()
        values['body'] = 'test ban 2'
        self.client.post(url, values, follow=True)
        self.assertEqual(len(Post.objects.filter(body='test ban 2')), 0)

    def get_csrf(self, form):
        return form.xpath('//input[@name="csrfmiddlewaretoken"]/@value')[0]

    def test_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username='zeus', password='zeus')
        post_url = reverse('pybb:add_post', kwargs={'topic_id': self.topic.id})
        response = client.get(post_url)
        values = self.get_form_values(response)
        del values['csrfmiddlewaretoken']
        response = client.post(post_url, values, follow=True)
        self.assertNotEqual(response.status_code, 200)
        response = client.get(self.topic.get_absolute_url())
        values = self.get_form_values(response)
        response = client.post(reverse('pybb:add_post', kwargs={'topic_id': self.topic.id}), values, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_blocking(self):
        user = get_user_model().objects.create_user('test', 'test@localhost', 'test')
        self.user.is_superuser = True
        self.user.save()
        self.login_client()
        self.assertEqual(self.client.get(reverse('pybb:block_user', args=[user.email]), follow=True).status_code, 200)
        user = get_user_model().objects.get(username=user.email)
        self.assertFalse(user.is_active)

    def test_headline(self):
        self.forum.headline = 'test <b>headline</b>'
        self.forum.save()
        client = Client()
        self.assertContains(client.get(self.forum.get_absolute_url()), 'test <b>headline</b>')

    def test_quote(self):
        self.login_client()
        response = self.client.get(reverse('pybb:add_post', kwargs={'topic_id': self.topic.id}), data={'quote_id': self.post.id, 'body': 'test tracking'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.body)

    def test_edit_post(self):
        self.login_client()
        edit_post_url = reverse('pybb:edit_post', kwargs={'pk': self.post.id})
        response = self.client.get(edit_post_url)
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.content)
        values = dict(tree.xpath('//form[@method="post"]')[0].form_values())
        values['body'] = 'test edit'
        response = self.client.post(edit_post_url, data=values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.get(pk=self.post.id).body, 'test edit')
        response = self.client.get(self.post.get_absolute_url(), follow=True)
        self.assertContains(response, 'test edit')

        # Check admin form
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(edit_post_url)
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.content)
        values = dict(tree.xpath('//form[@method="post"]')[0].form_values())
        values['body'] = 'test edit'
        values['login'] = 'new_login'
        response = self.client.post(edit_post_url, data=values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test edit')

    def test_admin_post_add(self):
        self.user.is_staff = True
        self.user.save()
        self.login_client()
        response = self.client.post(reverse('pybb:add_post', kwargs={'topic_id': self.topic.id}), data={'quote_id': self.post.id, 'body': 'test admin post', 'user': 'zeus'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test admin post')

    def test_stick(self):
        self.user.is_superuser = True
        self.user.save()
        self.login_client()
        self.assertEqual(self.client.get(reverse('pybb:stick_topic', kwargs={'pk': self.topic.id}), follow=True).status_code, 200)
        self.assertEqual(self.client.get(reverse('pybb:unstick_topic', kwargs={'pk': self.topic.id}), follow=True).status_code, 200)

    def test_delete_view(self):
        post = Post(topic=self.topic, user=self.user, body='test to delete')
        post.save()
        self.user.is_superuser = True
        self.user.save()
        self.login_client()
        response = self.client.post(reverse('pybb:delete_post', args=[post.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that topic and forum exists ;)
        self.assertEqual(Topic.objects.filter(id=self.topic.id).count(), 1)
        self.assertEqual(Forum.objects.filter(id=self.forum.id).count(), 1)

        # Delete topic
        response = self.client.post(reverse('pybb:delete_post', args=[self.post.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 0)
        self.assertEqual(Topic.objects.filter(id=self.topic.id).count(), 0)
        self.assertEqual(Forum.objects.filter(id=self.forum.id).count(), 1)

    def test_open_close(self):
        self.user.is_superuser = True
        self.user.save()
        self.login_client()
        add_post_url = reverse('pybb:add_post', args=[self.topic.id])
        response = self.client.get(add_post_url)
        values = self.get_form_values(response)
        values['body'] = 'test closed'
        response = self.client.get(reverse('pybb:close_topic', args=[self.topic.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(add_post_url, values, follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('pybb:open_topic', args=[self.topic.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(add_post_url, values, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_topic_updated(self):
        topic = Topic(name='etopic', forum=self.forum, user=self.user)
        topic.save()
        time.sleep(1)
        post = Post(topic=topic, user=self.user, body='bbcode [b]test[b]')
        post.save()
        client = Client()
        response = client.get(self.forum.get_absolute_url())
        self.assertEqual(response.context['topic_list'][0], topic)
        time.sleep(1)
        post = Post(topic=self.topic, user=self.user, body='bbcode [b]test[b]')
        post.save()
        client = Client()
        response = client.get(self.forum.get_absolute_url())
        self.assertEqual(response.context['topic_list'][0], self.topic)

    def test_topic_deleted(self):
        forum_1 = Forum.objects.create(name='new forum', category=self.category)
        topic_1 = Topic.objects.create(name='new topic', forum=forum_1, user=self.user)
        post_1 = Post.objects.create(topic=topic_1, user=self.user, body='test')
        time.sleep(2)
        self.assertEqual(topic_1.updated, post_1.created)
        self.assertEqual(forum_1.updated, post_1.created)

        topic_2 = Topic.objects.create(name='another topic', forum=forum_1, user=self.user)
        post_2 = Post.objects.create(topic=topic_2, user=self.user, body='another test')
        time.sleep(2)
        self.assertEqual(topic_2.updated, post_2.created)
        self.assertEqual(forum_1.updated, post_2.created)

        topic_2.delete()
        self.assertEqual(forum_1.updated, post_1.created)
        self.assertEqual(forum_1.topic_count, 1)
        self.assertEqual(forum_1.post_count, 1)

        post_1.delete()
        self.assertEqual(forum_1.topic_count, 0)
        self.assertEqual(forum_1.post_count, 0)

    def test_user_view(self):
        resp = self.client.get(reverse('pybb:user', kwargs={'username': self.user.email}))
        self.assertEqual(resp.status_code, 200)

    def test_post_count(self):
        topic = Topic(name='etopic', forum=self.forum, user=self.user)
        topic.save()
        post = Post(topic=topic, user=self.user, body='test') # another post
        post.save()
        self.assertEqual(self.user.profile.post_count, 2)
        post.body = 'test2'
        post.save()
        self.assertEqual(Profile.objects.get(pk=self.user.profile.pk).post_count, 2)
        post.delete()
        self.assertEqual(Profile.objects.get(pk=self.user.profile.pk).post_count, 1)

    def tearDown(self):
        defaults.PYBB_ENABLE_ANONYMOUS_POST = self.ORIG_PYBB_ENABLE_ANONYMOUS_POST
        defaults.PYBB_PREMODERATION = self.ORIG_PYBB_PREMODERATION


class AnonymousTest(TestCase, SharedTestModule):

    def setUp(self):
        self.ORIG_PYBB_ENABLE_ANONYMOUS_POST = defaults.PYBB_ENABLE_ANONYMOUS_POST
        self.ORIG_PYBB_ANONYMOUS_USERNAME = defaults.PYBB_ANONYMOUS_USERNAME
        defaults.PYBB_ENABLE_ANONYMOUS_POST = True
        defaults.PYBB_ANONYMOUS_USERNAME = 'Anonymous'
        self.user = get_user_model().objects.create_user('Anonymous', 'Anonymous@localhost', 'Anonymous')
        self.category = Category.objects.create(name='foo')
        self.forum = Forum.objects.create(name='xfoo', description='bar', category=self.category)
        self.topic = Topic.objects.create(name='etopic', forum=self.forum, user=self.user)
        add_post_permission = Permission.objects.get_by_natural_key('add_post', 'pybb', 'post')
        self.user.user_permissions.add(add_post_permission)

    def test_anonymous_posting(self):
        post_url = reverse('pybb:add_post', kwargs={'topic_id': self.topic.id})
        response = self.client.get(post_url)
        values = self.get_form_values(response)
        values['body'] = 'test anonymous'
        response = self.client.post(post_url, values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Post.objects.filter(body='test anonymous')), 1)
        self.assertEqual(Post.objects.get(body='test anonymous').user, self.user)

    def tearDown(self):
        defaults.PYBB_ENABLE_ANONYMOUS_POST = self.ORIG_PYBB_ENABLE_ANONYMOUS_POST
        defaults.PYBB_ANONYMOUS_USERNAME = self.ORIG_PYBB_ANONYMOUS_USERNAME


def premoderate_test(user, post):
    """
    Test premoderate function
    Allow post without moderation for staff users only
    """
    if user.email.startswith('allowed'):
        return True
    return False

class PreModerationTest(TestCase, SharedTestModule):

    def setUp(self):
        self.ORIG_PYBB_PREMODERATION = defaults.PYBB_PREMODERATION
        defaults.PYBB_PREMODERATION = premoderate_test
        self.create_user()
        self.create_initial()
        mail.outbox = []

    def test_premoderation(self):
        self.client.login(username='zeus', password='zeus')
        add_post_url = reverse('pybb:add_post', kwargs={'topic_id': self.topic.id})
        response = self.client.get(add_post_url)
        values = self.get_form_values(response)
        values['body'] = 'test premoderation'
        response = self.client.post(add_post_url, values, follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(body='test premoderation')
        self.assertEqual(post.on_moderation, True)

        # Post is visible by author
        response = self.client.get(post.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test premoderation')

        # Post is not visible by others
        client = Client()
        response = client.get(post.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 404)
        response = client.get(self.topic.get_absolute_url(), follow=True)
        self.assertNotContains(response, 'test premoderation')

        # But visible by superuser (with permissions)
        user = get_user_model().objects.create_user('admin', 'zeus@localhost', 'admin')
        user.is_superuser = True
        user.save()
        client.login(username='admin', password='admin')
        response = client.get(post.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test premoderation')

        # user with names stats with allowed can post without premoderation
        user = get_user_model().objects.create_user('allowed_zeus', 'zeus@localhost', 'allowed_zeus')
        client.login(username='allowed_zeus', password='allowed_zeus')
        response = client.get(add_post_url)
        values = self.get_form_values(response)
        values['body'] = 'test premoderation staff'
        response = client.post(add_post_url, values, follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(body='test premoderation staff')
        client = Client()
        response = client.get(post.get_absolute_url(), follow=True)
        self.assertContains(response, 'test premoderation staff')

        # Superuser can moderate
        user.is_superuser = True
        user.save()
        admin_client = Client()
        admin_client.login(username='admin', password='admin')
        post = Post.objects.get(body='test premoderation')
        response = admin_client.get(reverse('pybb:moderate_post', kwargs={'pk': post.id}), follow=True)
        self.assertEqual(response.status_code, 200)

        # Now all can see this post:
        client = Client()
        response = client.get(post.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test premoderation')

        # Other users can't moderate
        post.on_moderation = True
        post.save()
        client.login(username='zeus', password='zeus')
        response = client.get(reverse('pybb:moderate_post', kwargs={'pk': post.id}), follow=True)
        self.assertEqual(response.status_code, 403)

        # If user create new topic it goes to moderation if MODERATION_ENABLE
        # When first post is moderated, topic becomes moderated too
        self.client.login(username='zeus', password='zeus')
        add_topic_url = reverse('pybb:add_topic', kwargs={'forum_id': self.forum.id})
        response = self.client.get(add_topic_url)
        values = self.get_form_values(response)
        values['body'] = 'new topic test'
        values['name'] = 'new topic name'
        response = self.client.post(add_topic_url, values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'new topic test')

        client = Client()
        response = client.get(self.forum.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'new topic name')
        response = client.get(Topic.objects.get(name='new topic name').get_absolute_url())
        self.assertEqual(response.status_code, 404)
        response = admin_client.get(reverse('pybb:moderate_post',
                                     kwargs={'pk': Post.objects.get(body='new topic test').id}),
                                     follow=True)
        self.assertEqual(response.status_code, 200)

        response = client.get(self.forum.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'new topic name')
        response = client.get(Topic.objects.get(name='new topic name').get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        defaults.PYBB_PREMODERATION = self.ORIG_PYBB_PREMODERATION


class FiltersTest(TestCase, SharedTestModule):
    def setUp(self):
        self.create_user()
        self.create_initial(post=False)

    def test_filters(self):
        add_post_url = reverse('pybb:add_post', kwargs={'topic_id': self.topic.id})
        self.login_client()
        response = self.client.get(add_post_url)
        values = self.get_form_values(response)
        values['body'] = u'test\n \n \n\nmultiple empty lines\n'
        response = self.client.post(add_post_url, values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.all()[0].body, u'test\nmultiple empty lines')

from pybb import permissions
from django.db.models import Q

class CustomPermissionHandler(permissions.DefaultPermissionHandler):
    """
    a custom permission handler which changes the meaning of "hidden" forum:
    "hidden" forum or category is visible for all logged on users, not only staff
    """

    def filter_categories(self, user, qs):
        return qs.filter(hidden=False) if user.is_anonymous() else qs

    def filter_forums(self, user, qs):
        if user.is_anonymous():
            qs = qs.filter(Q(hidden=False)&Q(category__hidden=False))
        return qs

    def filter_topics(self, user, qs):
        if user.is_anonymous():
            qs = qs.filter(Q(forum__hidden=False)&Q(forum__category__hidden=False))
        return qs

    def filter_posts(self, user, qs):
        if user.is_anonymous():
            qs = qs.filter(Q(topic__forum__hidden=False)&Q(topic__forum__category__hidden=False))
        return qs

class CustomPermissionHandlerTest(TestCase, SharedTestModule):
    """ test custom permission handler """

    def setUp(self):
        from pybb import views
        self.create_user()
        # create public and hidden categories, forums, posts
        c_pub = Category(name='public'); c_pub.save()
        c_hid = Category(name='private', hidden=True); c_hid.save()
        Forum(name='pub1', category=c_pub).save()
        Forum(name='priv1', category=c_hid).save()
        Forum(name='private_in_public_cat', hidden=True, category=c_pub).save()
        for f in Forum.objects.all():
            t = Topic(name='a topic', forum=f, user=self.user)
            t.save()
            Post(topic=t, user=self.user, body='test').save()

        # override the permission handler. this cannot be done with @override_settings as
        # permissions.perms is already imported at this point, instead we got to monkeypatch
        # the modules (not really nice, but only an issue in tests)
        views.perms = permissions.perms = permissions._resolve_class('pybb.tests.CustomPermissionHandler')

    def tearDown(self):
        from pybb import views
        # reset permission handler (otherwise other tests may fail)
        views.perms = permissions.perms = permissions._resolve_class('pybb.permissions.DefaultPermissionHandler')

    def _get_with_user(self, url, username=None, password=None):
        if username:
            self.client.login(username=username, password=password)
        r = self.client.get(url,follow=True)
        self.client.logout()
        return r

    def test_category_permission(self):
        for c in Category.objects.all():
            # anon user may not see category
            r=self._get_with_user(c.get_absolute_url())
            if c.hidden:
                self.assertEqual(r.status_code, 404)
            else:
                self.assertEqual(r.status_code, 200)
            # logged on user may see all categories
            r=self._get_with_user(c.get_absolute_url(), 'zeus', 'zeus')
            self.assertEqual(r.status_code, 200)

    def test_forum_permission(self):
        for f in Forum.objects.all():
            r=self._get_with_user(f.get_absolute_url())
            self.assertEqual(r.status_code, 404 if f.hidden or f.category.hidden else 200)
            r=self._get_with_user(f.get_absolute_url(), 'zeus', 'zeus')
            self.assertEqual(r.status_code, 200)

    def test_topic_permission(self):
        for t in Topic.objects.all():
            r=self._get_with_user(t.get_absolute_url())
            self.assertEqual(r.status_code, 404 if t.forum.hidden or t.forum.category.hidden else 200)
            r=self._get_with_user(t.get_absolute_url(), 'zeus', 'zeus')
            self.assertEqual(r.status_code, 200)

    def test_post_permission(self):
        for p in Post.objects.all():
            r=self._get_with_user(p.get_absolute_url())
            self.assertEqual(r.status_code, 404 if p.topic.forum.hidden or p.topic.forum.category.hidden else 200)
            r=self._get_with_user(p.get_absolute_url(), 'zeus', 'zeus')
            self.assertEqual(r.status_code, 200)

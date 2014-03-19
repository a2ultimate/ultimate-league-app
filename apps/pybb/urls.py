# -*- coding: utf-8 -*-

from django.conf.urls import *

from pybb.feeds import LastPosts, LastTopics
from pybb.views import IndexView, CategoryView, ForumView, TopicView,\
    AddPostView, EditPostView, UserView, PostView,\
    DeletePostView, StickTopicView, UnstickTopicView, CloseTopicView,\
    OpenTopicView, ModeratePost, TopicPollVoteView, LatestTopicsView


urlpatterns = patterns('',
                       # Syndication feeds
                       url('^feeds/posts/$', LastPosts(), name='feed_posts'),
                       url('^feeds/topics/$', LastTopics(), name='feed_topics'),
                       )

urlpatterns += patterns('pybb.views',
                        # Index, Category, Forum
                        url('^$', IndexView.as_view(), name='index'),
                        url('^category/(?P<pk>\d+)/$', CategoryView.as_view(), name='category'),
                        url('^forum/(?P<pk>\d+)/$', ForumView.as_view(), name='forum'),

                        # User
                        url('^users/(?P<username>[^/]+)/$', UserView.as_view(), name='user'),
                        url('^block_user/([^/]+)/$', 'block_user', name='block_user'),

                        # Topic
                        url('^topic/(?P<pk>\d+)/$', TopicView.as_view(), name='topic'),
                        url('^topic/(?P<pk>\d+)/stick/$', StickTopicView.as_view(), name='stick_topic'),
                        url('^topic/(?P<pk>\d+)/unstick/$', UnstickTopicView.as_view(), name='unstick_topic'),
                        url('^topic/(?P<pk>\d+)/close/$', CloseTopicView.as_view(), name='close_topic'),
                        url('^topic/(?P<pk>\d+)/open/$', OpenTopicView.as_view(), name='open_topic'),
                        url('^topic/(?P<pk>\d+)/poll_vote/$', TopicPollVoteView.as_view(), name='topic_poll_vote'),
                        url('^topic/latest/$', LatestTopicsView.as_view(), name='topic_latest'),

                        # Add topic/post
                        url('^forum/(?P<forum_id>\d+)/topic/add/$', AddPostView.as_view(), name='add_topic'),
                        url('^topic/(?P<topic_id>\d+)/post/add/$', AddPostView.as_view(), name='add_post'),

                        # Post
                        url('^post/(?P<pk>\d+)/$', PostView.as_view(), name='post'),
                        url('^post/(?P<pk>\d+)/edit/$', EditPostView.as_view(), name='edit_post'),
                        url('^post/(?P<pk>\d+)/delete/$', DeletePostView.as_view(), name='delete_post'),
                        url('^post/(?P<pk>\d+)/moderate/$', ModeratePost.as_view(), name='moderate_post'),

                        )

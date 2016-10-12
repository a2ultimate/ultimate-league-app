# -*- coding: utf-8 -*-

import math

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_protect

try:
    from django.views import generic
except ImportError:
    try:
        from cbv import generic
    except ImportError:
        raise ImportError('If you using django version < 1.3 you should install django-cbv for pybb')

from pure_pagination import Paginator

from pybb.models import Category, Forum, Topic, Post
from pybb.forms import  PostForm, AdminPostForm
from pybb import defaults

from pybb.permissions import perms

class IndexView(generic.ListView):

    template_name = 'pybb/index.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        categories = ctx['categories']
        for category in categories:
            category.forums_accessed = perms.filter_forums(self.request.user, category.forums.all())
        ctx['categories'] = categories
        return ctx

    def get_queryset(self):
        return perms.filter_categories(self.request.user, Category.objects.all())

class CategoryView(generic.DetailView):

    template_name = 'pybb/index.html'
    context_object_name = 'category'

    def get_queryset(self):
        return perms.filter_categories(self.request.user, Category.objects.all())

    def get_context_data(self, **kwargs):
        ctx = super(CategoryView, self).get_context_data(**kwargs)
        ctx['category'].forums_accessed = perms.filter_forums(self.request.user, ctx['category'].forums.all())
        ctx['categories'] = [ctx['category']]
        return ctx

class ForumView(generic.ListView):

    paginate_by = defaults.PYBB_FORUM_PAGE_SIZE
    context_object_name = 'topic_list'
    template_name = 'pybb/forum.html'
    paginator_class = Paginator

    def get_context_data(self, **kwargs):
        ctx = super(ForumView, self).get_context_data(**kwargs)
        ctx['forum'] = self.forum
        return ctx

    def get_queryset(self):
        self.forum = get_object_or_404(perms.filter_forums(self.request.user, Forum.objects.all()), pk=self.kwargs['pk'])
        qs = self.forum.topics.order_by('-sticky', '-updated').select_related()
        if not (self.request.user.is_superuser or self.request.user in self.forum.moderators.all()):
            if self.request.user.is_authenticated():
                qs = qs.filter(Q(user=self.request.user)|Q(on_moderation=False))
            else:
                qs = qs.filter(on_moderation=False)
        return qs


class LatestTopicsView(generic.ListView):

    paginate_by = defaults.PYBB_FORUM_PAGE_SIZE
    context_object_name = 'topic_list'
    template_name = 'pybb/latest_topics.html'
    paginator_class = Paginator

    def get_queryset(self):
        qs = Topic.objects.all().select_related()
        qs = perms.filter_topics(self.request.user, qs)
        return qs.order_by('-updated')


class TopicView(generic.ListView):
    paginate_by = defaults.PYBB_TOPIC_PAGE_SIZE
    template_object_name = 'post_list'
    template_name = 'pybb/topic.html'
    paginator_class = Paginator

    def get_queryset(self):
        self.topic = get_object_or_404(perms.filter_topics(self.request.user, Topic.objects.select_related('forum')), pk=self.kwargs['pk'])
        self.topic.views += 1
        self.topic.save()
        qs = self.topic.posts.all().select_related('user')
        if not perms.may_moderate_topic(self.request.user, self.topic):
            qs = perms.filter_posts(self.request.user, qs)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(TopicView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            self.request.user.is_moderator = self.request.user.is_superuser or (self.request.user in self.topic.forum.moderators.all())
            if perms.may_post_as_admin(self.request.user):
                ctx['form'] = AdminPostForm(initial={'login': self.request.user.email}, topic=self.topic)
            else:
                ctx['form'] = PostForm(topic=self.topic)
        elif defaults.PYBB_ENABLE_ANONYMOUS_POST:
            ctx['form'] = PostForm(topic=self.topic)
        else:
            ctx['form'] = None
        if defaults.PYBB_FREEZE_FIRST_POST:
            ctx['first_post'] = self.topic.head
        else:
            ctx['first_post'] = None
        ctx['topic'] = self.topic

        return ctx


class PostEditMixin(object):

    def get_form_class(self):
        if perms.may_post_as_admin(self.request.user):
            return AdminPostForm
        else:
            return PostForm

    def get_context_data(self, **kwargs):
        ctx = super(PostEditMixin, self).get_context_data(**kwargs)
        return ctx

    def form_valid(self, form):
        success = True
        self.object = form.save(commit=False)

        if success:
            self.object.topic.save()
            self.object.topic = self.object.topic
            self.object.save()
            return super(ModelFormMixin, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AddPostView(PostEditMixin, generic.CreateView):

    template_name = 'pybb/add_post.html'

    def get_form_kwargs(self):
        ip = self.request.META.get('REMOTE_ADDR', '')
        form_kwargs = super(AddPostView, self).get_form_kwargs()
        form_kwargs.update(dict(topic=self.topic, forum=self.forum, user=self.user,
                       ip=ip, initial={}))
        if 'quote_id' in self.request.GET:
            try:
                quote_id = int(self.request.GET.get('quote_id'))
            except TypeError:
                raise Http404
            else:
                post = get_object_or_404(Post, pk=quote_id)
                quote = defaults.PYBB_QUOTE_ENGINES[defaults.PYBB_MARKUP](post.body, post.user.email)
                form_kwargs['initial']['body'] = quote
        if self.user.is_staff:
            form_kwargs['initial']['login'] = self.user.email
        return form_kwargs

    def get_context_data(self, **kwargs):
        ctx = super(AddPostView, self).get_context_data(**kwargs)
        ctx['forum'] = self.forum
        ctx['topic'] = self.topic
        return ctx

    def get_success_url(self):
        if (not self.request.user.is_authenticated()) and defaults.PYBB_PREMODERATION:
            return reverse('pybb:index')
        return super(AddPostView, self).get_success_url()

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self.user = request.user
        else:
            if defaults.PYBB_ENABLE_ANONYMOUS_POST:
                self.user, new = get_user_model().objects.get_or_create(username=defaults.PYBB_ANONYMOUS_USERNAME)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

        self.forum = None
        self.topic = None
        if 'forum_id' in kwargs:
            self.forum = get_object_or_404(perms.filter_forums(request.user, Forum.objects.all()), pk=kwargs['forum_id'])
            if not perms.may_create_topic(self.user, self.forum):
                raise PermissionDenied
        elif 'topic_id' in kwargs:
            self.topic = get_object_or_404(perms.filter_topics(request.user, Topic.objects.all()), pk=kwargs['topic_id'])
            if not perms.may_create_post(self.user, self.topic):
                raise PermissionDenied
        return super(AddPostView, self).dispatch(request, *args, **kwargs)

class EditPostView(PostEditMixin, generic.UpdateView):

    model = Post

    context_object_name = 'post'
    template_name = 'pybb/edit_post.html'

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(EditPostView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super(EditPostView, self).get_object(queryset)
        if not perms.may_edit_post(self.request.user, post):
            raise PermissionDenied
        return post


class UserView(generic.DetailView):
    model = get_user_model()
    template_name = 'pybb/user.html'
    context_object_name = 'target_user'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        ctx = super(UserView, self).get_context_data(**kwargs)
        ctx['topic_count'] = Topic.objects.filter(user=ctx['target_user']).count()
        return ctx


class PostView(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        post = get_object_or_404(perms.filter_posts(self.request.user, Post.objects.all()), pk=self.kwargs['pk'])
        count = post.topic.posts.filter(created__lt=post.created).count() + 1
        page = math.ceil(count / float(defaults.PYBB_TOPIC_PAGE_SIZE))
        return '%s?page=%d#post-%d' % (reverse('pybb:topic', args=[post.topic.id]), page, post.id)


class ModeratePost(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if not perms.may_moderate_topic(self.request.user, post.topic):
            raise PermissionDenied
        post.on_moderation = False
        post.save()
        return post.get_absolute_url()


class DeletePostView(generic.DeleteView):

    template_name = 'pybb/delete_post.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post.objects.select_related('topic', 'topic__forum'), pk=self.kwargs['pk'])
        if not perms.may_delete_post(self.request.user, post):
            raise PermissionDenied
        self.topic = post.topic
        self.forum = post.topic.forum
        if not perms.may_moderate_topic(self.request.user, self.topic):
            raise PermissionDenied
        return post

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        redirect_url = self.get_success_url()
        if not request.is_ajax():
            return HttpResponseRedirect(redirect_url)
        else:
            return HttpResponse(redirect_url)

    def get_success_url(self):
        try:
            Topic.objects.get(pk=self.topic.id)
        except Topic.DoesNotExist:
            return self.forum.get_absolute_url()
        else:
            if not self.request.is_ajax():
                return self.topic.get_absolute_url()
            else:
                return ""


class TopicActionBaseView(generic.View):

    def get_topic(self):
        return get_object_or_404(Topic, pk=self.kwargs['pk'])

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        self.topic = self.get_topic()
        self.action(self.topic)
        return HttpResponseRedirect(self.topic.get_absolute_url())

class StickTopicView(TopicActionBaseView):

    def action(self, topic):
        if not perms.may_stick_topic(self.request.user, topic):
            raise PermissionDenied
        topic.sticky = True
        topic.save()


class UnstickTopicView(TopicActionBaseView):

    def action(self, topic):
        if not perms.may_unstick_topic(self.request.user, topic):
            raise PermissionDenied
        topic.sticky = False
        topic.save()


class CloseTopicView(TopicActionBaseView):

    def action(self, topic):
        if not perms.may_close_topic(self.request.user, topic):
            raise PermissionDenied
        topic.closed = True
        topic.save()


class OpenTopicView(TopicActionBaseView):
    def action(self, topic):
        if not perms.may_open_topic(self.request.user, topic):
            raise PermissionDenied
        topic.closed = False
        topic.save()


@login_required
def block_user(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if not perms.may_block_user(request.user, user):
        raise PermissionDenied
    user.is_active = False
    user.save()
    msg = _('User successfuly blocked')
    messages.success(request, msg, fail_silently=True)
    return redirect('pybb:index')

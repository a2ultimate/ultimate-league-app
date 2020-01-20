from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class NewsArticle(models.Model):
    NEWS_TYPE_HTML = 'html'
    NEWS_TYPE_MARKDOWN = 'markdown'
    NEWS_TYPE_PLAIN = 'plain'
    NEWS_TYPE_CHOICES = (
        (NEWS_TYPE_HTML, 'HTML'),
        (NEWS_TYPE_MARKDOWN, 'Markdown'),
        (NEWS_TYPE_PLAIN, 'Plain'),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    url = models.SlugField(null=True, blank=True)
    type = models.CharField(max_length=8, choices=NEWS_TYPE_CHOICES)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_article'
        ordering = ['-published', '-created', '-updated']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        idOrUrl = self.url if self.url else self.id
        return reverse('news_acticle', kwargs={'url': idOrUrl})

    def save(self):
        if not self.url:
            self.url = slugify(self.title[:50])

        super(NewsArticle, self).save()

    @property
    def is_html(self):
        return self.type == self.NEWS_TYPE_HTML

    @property
    def is_markdown(self):
        return self.type == self.NEWS_TYPE_MARKDOWN

    @property
    def is_plain(self):
        return self.type == self.NEWS_TYPE_PLAIN

    @property
    def is_published(self):
        return self.published <= timezone.now()



class StaticContent(models.Model):
    STATIC_CONTENT_TYPE_HTML = 'html'
    STATIC_CONTENT_TYPE_MARKDOWN = 'markdown'
    STATIC_CONTENT_TYPE_PLAIN = 'plain'
    STATIC_CONTENT_TYPE_CHOICES = (
        (STATIC_CONTENT_TYPE_HTML, 'HTML'),
        (STATIC_CONTENT_TYPE_MARKDOWN, 'Markdown'),
        (STATIC_CONTENT_TYPE_PLAIN, 'Plain'),
    )

    id = models.AutoField(primary_key=True)
    url = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=765)
    type = models.CharField(max_length=32, choices=STATIC_CONTENT_TYPE_CHOICES)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'static_content'
        verbose_name_plural = 'static content'

    def __unicode__(self):
        return self.url

    def get_absolute_url(self):
        return reverse('static_page', kwargs={'content_url': self.url})

    @property
    def is_html(self):
        return self.type == self.STATIC_CONTENT_TYPE_HTML

    @property
    def is_markdown(self):
        return self.type == self.STATIC_CONTENT_TYPE_MARKDOWN

    @property
    def is_plain(self):
        return self.type == self.STATIC_CONTENT_TYPE_PLAIN


class StaticMenuItems(models.Model):
    STATIC_MENU_ITEM_TYPES = (
        ('header', 'Header'),
        ('external_link', 'External Link'),
        ('internal_link', 'Internal Link'),
        ('static_link', 'Static Link'),
        ('text', 'Text'),
    )

    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=32)
    type = models.CharField(max_length=32, choices=STATIC_MENU_ITEM_TYPES)
    content = models.CharField(max_length=64)
    href = models.CharField(max_length=255, blank=True)
    position = models.IntegerField()
    parent = models.ForeignKey('index.StaticMenuItems', default=None, blank=True, null=True)

    class Meta:
        db_table = 'static_menu_items'
        ordering = ['location', 'parent__id', 'position']
        verbose_name_plural = 'static menu items'

    def __unicode__(self):
        return self.content

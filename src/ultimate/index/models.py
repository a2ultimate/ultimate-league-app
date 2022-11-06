from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class NewsArticle(models.Model):
    NEWS_TYPE_MARKDOWN = 'markdown'
    NEWS_TYPE_HTML = 'html'
    NEWS_TYPE_PLAIN = 'plain'
    NEWS_TYPE_CHOICES = (
        (NEWS_TYPE_MARKDOWN, 'Markdown'),
        (NEWS_TYPE_HTML, 'HTML'),
        (NEWS_TYPE_PLAIN, 'Plain'),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    url = models.SlugField(null=True, blank=True)
    type = models.CharField(max_length=8, choices=NEWS_TYPE_CHOICES, help_text='<a href="https://www.markdownguide.org/basic-syntax/" target="_blank">Get Help with Markdown</a> | <a href="https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics" target="_blank">Get Help with HTML</a>')
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(help_text='Posts with a published date in the future will be hidden until that date')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_article'
        ordering = ['-published', '-created', '-updated']

    def __str__(self):
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
    STATIC_CONTENT_TYPE_MARKDOWN = 'markdown'
    STATIC_CONTENT_TYPE_HTML = 'html'
    STATIC_CONTENT_TYPE_PLAIN = 'plain'
    STATIC_CONTENT_TYPE_CHOICES = (
        (STATIC_CONTENT_TYPE_MARKDOWN, 'Markdown'),
        (STATIC_CONTENT_TYPE_HTML, 'HTML'),
        (STATIC_CONTENT_TYPE_PLAIN, 'Plain'),
    )

    id = models.AutoField(primary_key=True)
    url = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=765)
    type = models.CharField(max_length=32, choices=STATIC_CONTENT_TYPE_CHOICES, help_text='<a href="https://www.markdownguide.org/basic-syntax/" target="_blank">Get Help with Markdown</a> | <a href="https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics" target="_blank">Get Help with HTML</a>')
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'static_content'
        verbose_name_plural = 'static content'

    def __str__(self):
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
    STATIC_MENU_ITEM_TYPES_HEADER = 'header'
    STATIC_MENU_ITEM_TYPES_EXTERNAL = 'external_link'
    STATIC_MENU_ITEM_TYPES_INTERNAL = 'internal_link'
    STATIC_MENU_ITEM_TYPES_STATIC = 'static_link'
    STATIC_MENU_ITEM_TYPES_TEXT = 'text'
    STATIC_MENU_ITEM_TYPES_CHOICES = (
        (STATIC_MENU_ITEM_TYPES_HEADER, 'Header'),
        (STATIC_MENU_ITEM_TYPES_EXTERNAL, 'External Link'),
        (STATIC_MENU_ITEM_TYPES_INTERNAL, 'Internal Link'),
        (STATIC_MENU_ITEM_TYPES_STATIC, 'Static Link'),
        (STATIC_MENU_ITEM_TYPES_TEXT, 'Text'),
    )

    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=32)
    type = models.CharField(max_length=32, choices=STATIC_MENU_ITEM_TYPES_CHOICES, help_text='<ul><li>Header - text header for grouping content</li><li>External Link - link to an external page (set `href` field to a full web address starting with "https://")</li><li>Internal Link - link to a page on the website (set `href` field to a relative url starting with "/")</li><li>Static Link - link off to static content in the app (set `href` field to a relative url starting with "/")</li><li>Text - plain text</li></ul>')
    content = models.CharField(max_length=64, help_text="Text a user will see")
    href = models.CharField(max_length=255, blank=True, help_text='Use with "External Link", "Internal Link", and "Static Link"')
    position = models.IntegerField(help_text='Order of sibling items within a parent')
    parent = models.ForeignKey('index.StaticMenuItems', default=None, blank=True, null=True, help_text='Only "Header" type items can be parents')

    class Meta:
        db_table = 'static_menu_items'
        ordering = ['location', 'parent__id', 'position']
        verbose_name_plural = 'static menu items'

    def __str__(self):
        return self.content

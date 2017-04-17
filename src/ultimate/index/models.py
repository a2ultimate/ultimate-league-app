from django.db import models


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
        db_table = u'static_content'
        verbose_name_plural = 'static content'

    def __unicode__(self):
        return self.url

    def get_absolute_url(self):
        return '/{}'.format(self.url)

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
        ('header', u'Header'),
        ('external_link', u'External Link'),
        ('internal_link', u'Internal Link'),
        ('static_link', u'Static Link'),
        ('text', u'Text'),
    )

    id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=32)
    type = models.CharField(max_length=32, choices=STATIC_MENU_ITEM_TYPES)
    content = models.CharField(max_length=64)
    href = models.CharField(max_length=255, blank=True)
    position = models.IntegerField()
    parent = models.ForeignKey('index.StaticMenuItems', default=None, blank=True, null=True)

    class Meta:
        db_table = u'static_menu_items'
        ordering = ['location', 'parent__id', 'position']
        verbose_name_plural = 'static menu items'

    def __unicode__(self):
        return self.content

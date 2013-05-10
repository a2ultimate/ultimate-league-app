from django.db import models
from django.contrib.auth.models import User

class StaticContent(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.CharField(unique=True, max_length=255)
	title = models.CharField(max_length=765)
	content = models.TextField()
	nav_bar_id = models.IntegerField(unique=True, null=True, blank=True)
	class Meta:
		db_table = u'static_content'
		verbose_name_plural = 'static content'

	def __unicode__(self):
		return self.url
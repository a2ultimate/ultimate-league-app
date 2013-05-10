from django.contrib import admin
from ultimate.index.models import *


class StaticContentAdmin(admin.ModelAdmin):
	list_display = ('url', 'title',)
	list_display_links = ('url',)
	save_as = True
	save_on_top = True


admin.site.register(StaticContent, StaticContentAdmin)

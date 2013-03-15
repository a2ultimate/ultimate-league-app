from django.contrib import admin
from ultimate.leagues.models import *

class FieldAdmin(admin.ModelAdmin):
	js = (
		'js/getElementsBySelector.js',
		'filebrowser/js/AddFileBrowser.js',
	)
admin.site.register(Field, FieldAdmin)

class LeagueAdmin(admin.ModelAdmin):
	list_display = ('year', 'season', 'night', 'gender', 'state',)
	list_display_links = ('year', 'season', 'night', 'gender', 'state',)
	save_as = True
	save_on_top = True
	js = (
		'/media/js/tiny_mce/tiny_mce.js',
		'/media/js/textarea.js',
	)
admin.site.register(League, LeagueAdmin)

class ScheduleAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'score_report',)
	list_select_related = True
admin.site.register(Schedule, ScheduleAdmin)

admin.site.register(Game)
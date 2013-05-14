from django.contrib import admin
from ultimate.leagues.models import *


class LeagueAdmin(admin.ModelAdmin):
	list_display = ('year', 'season', 'night', 'gender', 'state',)
	list_display_links = ('year', 'season', 'night', 'gender', 'state',)
	save_as = True
	save_on_top = True

class RegistrationsAdmin(admin.ModelAdmin):
	list_display = ('league', 'user', 'created', 'updated', 'registered', 'attendance', 'captain', 'waitlist', 'get_status',)
	save_as = True
	save_on_top = True

class SkillsAdmin(admin.ModelAdmin):
	list_display = ('updated', 'skills_report', 'user', 'submitted_by',)
	save_as = True
	save_on_top = True


admin.site.register(Field)
admin.site.register(FieldNames)
admin.site.register(Game)
admin.site.register(League, LeagueAdmin)
admin.site.register(Registrations, RegistrationsAdmin)
admin.site.register(Skills, SkillsAdmin)
admin.site.register(Team)
admin.site.register(TeamMember)

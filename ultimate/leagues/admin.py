from django.contrib import admin
from ultimate.leagues.models import *


class LeagueAdmin(admin.ModelAdmin):
	save_as = True
	save_on_top = True

	list_display = ('year', 'season', 'night', 'gender', 'state',)
	list_display_links = ('year', 'season', 'night', 'gender', 'state',)
	list_filter = ('year', 'season', 'night', 'gender', 'state', )
	search_fields = ['year', 'season', 'night', 'gender',]


class RegistrationsAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('user', 'league', 'registered', 'paypal_complete', 'check_complete', 'refunded', 'attendance', 'captain',)
		}),
		('Advanced options', {
			'classes': ('collapse',),
			'fields': ('created', 'updated', 'conduct_complete', 'waiver_complete', 'pay_type', 'paypal_invoice_id', 'baggage',)
		}),
	)
	readonly_fields = ('created', 'updated',)
	save_as = True
	save_on_top = True

	list_display = ('year', 'season', 'night', 'user_details', 'registered', 'attendance', 'captain', 'waitlist', 'get_status',)
	list_filter = ('league__year', 'league__season', 'league__night', 'paypal_complete', 'check_complete', 'refunded',)
	search_fields = ['user__first_name', 'user__last_name', 'user__email',]

	def year(self, obj):
		return u'%d' % (obj.league.year)
	year.admin_order_field  = 'league__year'

	def season(self, obj):
		return u'%s' % (obj.league.season)
	season.admin_order_field  = 'league__season'

	def night(self, obj):
		return u'%s' % (obj.league.night)
	night.admin_order_field  = 'league__night'

	def user_details(self, obj):
		return u'%s <br /> %s' % (obj.user.get_full_name(), obj.user.email)
	user_details.allow_tags = True


class SkillsAdmin(admin.ModelAdmin):
	save_as = True
	save_on_top = True

	list_display = ('updated', 'skills_report', 'user_details', 'submitted_by_details',)

	def user_details(self, obj):
		return u'%s <br /> %s' % (obj.user.get_full_name(), obj.user.email)
	user_details.allow_tags = True

	def submitted_by_details(self, obj):
		return u'%s <br /> %s' % (obj.submitted_by.get_full_name(), obj.submitted_by.email)
	submitted_by_details.allow_tags = True


admin.site.register(Baggage)
admin.site.register(Field)
admin.site.register(FieldNames)
admin.site.register(Game)
admin.site.register(League, LeagueAdmin)
admin.site.register(Registrations, RegistrationsAdmin)
admin.site.register(Skills, SkillsAdmin)
admin.site.register(Team)
admin.site.register(TeamMember)

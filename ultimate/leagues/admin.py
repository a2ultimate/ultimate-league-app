from django import forms
from django.contrib import admin

from paypal.standard.ipn.models import PayPalIPN
from ultimate.leagues.models import *


class GameTeamsInline(admin.TabularInline):
	model = GameTeams
	max_num = 2

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'team' and request._game_obj_:
			kwargs['queryset'] = Team.objects.filter(league__id=request._game_obj_.league.id)
		else:
			kwargs['queryset'] = Team.objects.filter()
		return super(GameTeamsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class GameAdmin(admin.ModelAdmin):
	inlines = [GameTeamsInline,]
	save_as = True
	save_on_top = True

	list_display = ('date', 'league', 'field_name', 'game_teams',)
	list_filter = ('league__year', 'league__season', 'league__night', 'league__gender', 'league__state', )

	def get_form(self, request, obj=None, **kwargs):
		# just save obj reference for future processing in Inline
		request._game_obj_ = obj
		return super(GameAdmin, self).get_form(request, obj, **kwargs)

	def game_teams(self, obj):
		teams = []
		game_teams = obj.gameteams_set.all()

		for game_team in game_teams:
			teams.append(game_team.team.id)

		return ', '.join(map(str, teams))


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
			'fields': ('user', 'league', 'registered', 'paypal_complete', 'check_complete', 'waitlist', 'refunded', 'attendance', 'captain',)
		}),
		('Advanced Options', {
			'classes': ('collapse',),
			'fields': ('created', 'updated', 'conduct_complete', 'waiver_complete', 'pay_type', 'paypal_invoice_id', 'paypal_details', 'baggage',)
		}),
	)
	readonly_fields = ('created', 'updated', 'paypal_details',)
	save_as = True
	save_on_top = True

	list_display = ('year', 'season', 'night', 'user_details', 'registered', 'attendance', 'captain_value', 'waitlist', 'status',)
	list_filter = ('league__year', 'league__season', 'league__night', 'paypal_complete', 'check_complete', 'waitlist', 'refunded',)
	search_fields = ['user__first_name', 'user__last_name', 'user__email', 'paypal_invoice_id',]

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

	def captain_value(self, obj):
		return obj.captain
	captain_value.admin_order_field = 'captain'

	def paypal_details(self, obj):
		paypal_row = PayPalIPN.objects.get(invoice=obj.paypal_invoice_id)
		if not paypal_row:
			return None
		return u'Name: %s %s <br />Email: %s' % (paypal_row.first_name, paypal_row.last_name, paypal_row.payer_email)
	paypal_details.allow_tags = True


class TeamMemberModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, team_member):
		# Return a string of the format: "firstname lastname (username)"
		return '%s, %s (%s)' % (team_member.last_name, team_member.first_name, team_member.username)

	class Meta:
		label = ''


class TeamMemberInline(admin.TabularInline):
	model = TeamMember

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'user':
			kwargs['form_class'] = TeamMemberModelChoiceField

			if request._team_obj_:
				registration_user_ids = Registrations.objects.filter(league__id=request._team_obj_.league.id).values_list('user', flat=True)
				kwargs['queryset'] = User.objects.filter(id__in=registration_user_ids).order_by('last_name', 'email')
			else:
				kwargs['queryset'] = User.objects.filter().order_by('last_name', 'email')

			return db_field.formfield(**kwargs)

		return super(TeamMemberInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TeamAdmin(admin.ModelAdmin):
	inlines = [TeamMemberInline,]
	save_as = True
	save_on_top = True

	def get_form(self, request, obj=None, **kwargs):
		# just save obj reference for future processing in Inline
		request._team_obj_ = obj
		return super(TeamAdmin, self).get_form(request, obj, **kwargs)

	list_display = ('id', 'name', 'color', 'email', 'league', 'hidden',)
	list_editable = ('name', 'color', 'email',)
	list_filter = ('league__year', 'league__season', 'league__night', 'league__gender', 'league__state', 'hidden',)


admin.site.register(Baggage)
admin.site.register(Field)
admin.site.register(FieldNames)
admin.site.register(Game, GameAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(Registrations, RegistrationsAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember)

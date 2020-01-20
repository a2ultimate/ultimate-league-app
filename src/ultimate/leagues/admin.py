from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Max, Q

from paypal.standard.ipn.models import PayPalIPN
from ultimate.leagues.models import Coupon, CouponRedemtion, Field, FieldNames, GameTeams, Team, LeagueFields, Baggage, TeamMember, Registrations, Game, League, Season


class CouponRedemtionInline(admin.TabularInline):
    model = CouponRedemtion

class CouponAdmin(admin.ModelAdmin):
    inlines = [CouponRedemtionInline, ]
    list_display = ('code', 'note', 'type', 'value', 'use_count', 'created_at', )

    readonly_fields = ('created_by', 'created_at', 'updated_at', )
    save_as = True
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()


class FieldAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True

    list_display = ('name', 'layout_link', 'driving_link', 'type',)
    # list_editable = ('name', 'layout_link', 'driving_link', 'type',)
    list_filter = ('type',)


def mark_hidden(modeladmin, request, queryset):
    queryset.update(hidden=True)
mark_hidden.short_description = "Mark selected field names as hidden"

def mark_not_hidden(modeladmin, request, queryset):
    queryset.update(hidden=False)
mark_not_hidden.short_description = "Mark selected field names as not hidden"

class FieldNameAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True

    list_display = ('name', 'field', 'type', 'hidden',)
    list_filter = ('hidden', 'type', 'field__type', 'field',)

    actions = [mark_hidden, mark_not_hidden,]


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
    inlines = [GameTeamsInline, ]
    save_as = True
    save_on_top = True

    list_display = ('date', 'start', 'league', 'field_name', 'game_teams',)
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


class LeagueFieldsInline(admin.TabularInline):
    model = LeagueFields
    extra = 1


class LeagueAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True

    inlines = (LeagueFieldsInline,)
    list_display = ('id', 'year', 'season', 'night', 'gender', 'level', 'type', 'state',)
    list_display_links = ('id',)
    list_filter = ('year', 'season', 'night', 'gender', 'level', 'type', 'state', )
    ordering = ['-year', '-season__order', '-league_start_date']
    prepopulated_fields = {'night_slug': ('night',)}
    search_fields = ['year', 'season__name', 'season__slug', 'night', 'night_slug', 'gender',]


def mark_flagged(modeladmin, request, queryset):
    queryset.update(flagged=True)
mark_flagged.short_description = "Mark selected registrations as flagged"

def mark_not_flagged(modeladmin, request, queryset):
    queryset.update(flagged=False)
mark_not_flagged.short_description = "Mark selected registrations as not flagged"

def mark_refunded(modeladmin, request, queryset):
    queryset.update(refunded=True)
mark_refunded.short_description = "Mark selected registrations as refunded"

def mark_not_refunded(modeladmin, request, queryset):
    queryset.update(refunded=False)
mark_not_refunded.short_description = "Mark selected registrations as not refunded"

def mark_waitlisted(modeladmin, request, queryset):
    queryset.update(waitlist=True)
mark_waitlisted.short_description = "Mark selected registrations as waitlisted"

def mark_not_waitlisted(modeladmin, request, queryset):
    queryset.update(waitlist=False)
mark_not_waitlisted.short_description = "Mark selected registrations as not waitlisted"

class RegistrationsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'league', 'registered', 'payment_complete', 'paypal_complete', 'check_complete', 'coupon', 'waitlist', 'refunded', 'flagged', 'attendance', 'captain', 'baggage', 'prompt_response', 'paypal_details', )
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('created', 'updated', 'conduct_complete', 'waiver_complete', 'pay_type', 'paypal_invoice_id', )
        }),
    )
    readonly_fields = ('created', 'updated', 'paypal_details',)
    save_as = True
    save_on_top = True

    list_display = ('id', 'league', 'user_details', 'registered', 'waitlist', 'flagged', 'status',)
    list_filter = ('league__year', 'league__season', 'league__night', 'paypal_complete', 'check_complete', 'waitlist', 'refunded', 'flagged',)
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'paypal_invoice_id', 'baggage__id', 'coupon__code']

    actions = [mark_flagged, mark_not_flagged, mark_refunded, mark_not_refunded, mark_waitlisted, mark_not_waitlisted,]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._registration_obj_ = obj
        return super(RegistrationsAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'baggage' and request._registration_obj_:
            max_id = Baggage.objects.all().aggregate(Max('id'))['id__max']
            kwargs['queryset'] = Baggage.objects.filter(Q(registrations__league=request._registration_obj_.league) | Q(registrations__id__isnull=True)).order_by('id').distinct()
        return super(RegistrationsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def year(self, obj):
        return '{}'.format(obj.league.year)
    year.admin_order_field = 'league__year'

    def season(self, obj):
        return '{}'.format(obj.league.season)
    season.admin_order_field = 'league__season'

    def night(self, obj):
        return '{}'.format(obj.league.night)
    night.admin_order_field = 'league__night'

    def user_details(self, obj):
        return '{} <br /> {}'.format(obj.user.get_full_name(), obj.user.email)
    user_details.allow_tags = True

    def captain_value(self, obj):
        return obj.captain
    captain_value.admin_order_field = 'captain'

    def paypal_details(self, obj):
        paypal_row = PayPalIPN.objects.filter(invoice=obj.paypal_invoice_id).order_by('-payment_date')[:1].get()
        if not paypal_row:
            return None
        return 'Name: {} {}<br />Email: {}<br />Date: {}<br />Status: {}<br />Amount: {}'.format(paypal_row.first_name, paypal_row.last_name, paypal_row.payer_email, paypal_row.payment_date, paypal_row.payment_status, paypal_row.mc_gross)
    paypal_details.allow_tags = True


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'order',)
    prepopulated_fields = {'slug': ('name',),}
    save_as = True
    save_on_top = True


class TeamMemberModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, team_member):
        # Return a string of the format: "firstname lastname (username)"
        return '{}, {} ({})'.format(team_member.last_name, team_member.first_name, team_member.email)

    class Meta:
        label = ''


class TeamMemberInline(admin.TabularInline):
    model = TeamMember

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['form_class'] = TeamMemberModelChoiceField

            if request._team_obj_:
                registration_user_ids = Registrations.objects.filter(league__id=request._team_obj_.league.id).values_list('user', flat=True)
                kwargs['queryset'] = get_user_model().objects.filter(id__in=registration_user_ids).order_by('last_name', 'email')
            else:
                kwargs['queryset'] = get_user_model().objects.filter().order_by('last_name', 'email')

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
    # list_editable = ('name', 'color', 'email',)
    list_filter = ('league__year', 'league__season', 'league__night', 'league__gender', 'league__state', 'hidden',)


admin.site.register(Baggage)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(FieldNames, FieldNameAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(Registrations, RegistrationsAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Team, TeamAdmin)

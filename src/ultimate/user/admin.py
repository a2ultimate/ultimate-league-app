from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from hijack.contrib.admin import HijackUserAdminMixin
from paypal.standard.ipn.admin import PayPalIPNAdmin
from paypal.standard.ipn.models import PayPalIPN

from ultimate.user.models import Player, PlayerRatings, PlayerConcussionWaiver


class PlayerInline(admin.StackedInline):
    model = Player

    fieldsets = (
        (_('Profile'), {'fields': ('nickname', 'date_of_birth', 'gender', 'phone', 'zip_code',
                                   'height_inches', 'highest_level', 'jersey_size', 'guardian_name', 'guardian_email', 'guardian_phone',)}),
    )

    can_delete = False
    save_as = True
    save_on_top = True
    verbose_name_plural = 'player'


class UserAdmin(HijackUserAdminMixin, BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )

    inlines = (PlayerInline,)
    # django-hijack 3.x's HijackUserAdminMixin appends its own hijack column to
    # the changelist automatically; no explicit 'hijack_field' entry needed.
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_superuser', 'date_joined',)
    list_filter = BaseUserAdmin.list_filter + ('groups__name',)
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name',)


class PlayerRatingsAdmin(admin.ModelAdmin):
    save_as = True
    save_on_top = True

    list_display = ('updated', 'user_details',
                    'submitted_by_details', 'ratings_type',)
    list_filter = ('ratings_type',)
    readonly_fields = ('ratings_report',)
    search_fields = ['user__first_name', 'user__last_name', 'user__email',
                     'submitted_by__first_name', 'submitted_by__last_name', 'submitted_by__email',]

    def user_details(self, obj):
        return format_html('{} <br /> {}', obj.user.get_full_name(), obj.user.email)

    def submitted_by_details(self, obj):
        return format_html('{} <br /> {}', obj.submitted_by.get_full_name(), obj.submitted_by.email)


class PlayerConcussionWaiverAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ('submitted_by_details', 'submitted_at', 'reviewed_by_details', 'status',)
    list_filter = ('status',)
    readonly_fields = ('reviewed_by', 'reviewed_at', 'created', 'updated')
    search_fields = ['submitted_by__first_name', 'submitted_by__last_name', 'submitted_by__email',]

    def reviewed_by_details(self, obj):
        return format_html('{} <br /> {}', obj.reviewed_by.get_full_name(), obj.reviewed_by.email)

    def submitted_by_details(self, obj):
        return format_html('{} <br /> {}', obj.submitted_by.get_full_name(), obj.submitted_by.email)


class CustomPayPalIPNAdmin(PayPalIPNAdmin):
    search_fields = ['invoice', 'txn_id', 'recurring_payment_id', 'subscr_id',]


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(PlayerRatings, PlayerRatingsAdmin)
admin.site.register(PlayerConcussionWaiver, PlayerConcussionWaiverAdmin)

admin.site.unregister(PayPalIPN)
admin.site.register(PayPalIPN, CustomPayPalIPNAdmin)

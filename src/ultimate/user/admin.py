from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from hijack_admin.admin import HijackUserAdminMixin
from paypal.standard.ipn.admin import PayPalIPNAdmin
from paypal.standard.ipn.models import PayPalIPN

from ultimate.user.models import Player, PlayerRatings


class PlayerInline(admin.StackedInline):
    model = Player

    fieldsets = (
        (_('Profile'), {'fields': ('nickname', 'date_of_birth', 'gender', 'phone', 'zip_code',
                                   'height_inches', 'highest_level', 'jersey_size', 'guardian_name', 'guardian_phone',)}),
    )

    can_delete = False
    save_as = True
    save_on_top = True
    verbose_name_plural = 'player'


class UserAdmin(BaseUserAdmin, HijackUserAdminMixin):
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
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_superuser', 'date_joined',
                    'hijack_field',)
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
        return '{} <br /> {}'.format(obj.user.get_full_name(), obj.user.email)
    user_details.allow_tags = True

    def submitted_by_details(self, obj):
        return '{} <br /> {}'.format(obj.submitted_by.get_full_name(), obj.submitted_by.email)
    submitted_by_details.allow_tags = True


class CustomPayPalIPNAdmin(PayPalIPNAdmin):
    search_fields = ['invoice', 'txn_id', 'recurring_payment_id', 'subscr_id',]


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(PlayerRatings, PlayerRatingsAdmin)

admin.site.unregister(PayPalIPN)
admin.site.register(PayPalIPN, CustomPayPalIPNAdmin)

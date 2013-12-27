from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ultimate.user.models import *

class MyUserAdmin(UserAdmin):
	list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
	list_filter = UserAdmin.list_filter + ('groups__name',)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


class PlayerRatingsAdmin(admin.ModelAdmin):
	save_as = True
	save_on_top = True

	list_display = ('updated', 'user_details', 'submitted_by_details', 'ratings_type',)
	list_filter = ('ratings_type',)
	search_fields = ['user__first_name', 'user__last_name', 'user__email', 'submitted_by__first_name', 'submitted_by__last_name', 'submitted_by__email',]

	def user_details(self, obj):
		return u'%s <br /> %s' % (obj.user.get_full_name(), obj.user.email)
	user_details.allow_tags = True

	def submitted_by_details(self, obj):
		return u'%s <br /> %s' % (obj.submitted_by.get_full_name(), obj.submitted_by.email)
	submitted_by_details.allow_tags = True


admin.site.register(PlayerRatings, PlayerRatingsAdmin)

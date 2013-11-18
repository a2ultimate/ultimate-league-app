from django.contrib import admin
from ultimate.user.models import *

class PlayerRatingsAdmin(admin.ModelAdmin):
	save_as = True
	save_on_top = True

	list_display = ('updated', 'user_details', 'submitted_by_details',)

	def user_details(self, obj):
		return u'%s <br /> %s' % (obj.user.get_full_name(), obj.user.email)
	user_details.allow_tags = True

	def submitted_by_details(self, obj):
		return u'%s <br /> %s' % (obj.submitted_by.get_full_name(), obj.submitted_by.email)
	submitted_by_details.allow_tags = True

admin.site.register(PlayerRatings, PlayerRatingsAdmin)

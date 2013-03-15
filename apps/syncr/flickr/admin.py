from django.contrib import admin

from syncr.flickr.models import Photo, PhotoSet

class PhotoAdmin(admin.ModelAdmin):
	date_hierarchy = 'taken_date'
	list_display = ('taken_date', 'title', 'upload_date', 'flickr_id', 'owner')
	list_display_links = ('title', 'flickr_id')
	list_filter = ('upload_date', 'taken_date')
	prepopulated_fields = {'slug': ('title',)}
	search_fields = ['title', 'description']

class PhotoSetAdmin(admin.ModelAdmin):
	list_display = ('get_primary_photo', 'title', 'flickr_id', 'owner')
	list_display_links = ('title',)
	list_select_related = True # ``get_primary_photo`` uses a ForeignKey

admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoSet, PhotoSetAdmin)
from django.contrib import admin
from ultimate.index.models import (NewsArticle, StaticContent, StaticMenuItems)


class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'created', 'updated', 'is_published',)
    list_display_links = ('title',)
    prepopulated_fields = {'url': ('title',),}
    save_as = True
    save_on_top = True
    search_fields = ['title', 'content',]


class StaticContentAdmin(admin.ModelAdmin):
    list_display = ('url', 'title',)
    list_display_links = ('url',)
    save_as = True
    save_on_top = True


class StaticMenuItemsAdmin(admin.ModelAdmin):
    list_display = ('location', 'position', 'parent', 'content', 'href', 'type',)
    list_display_links = ('location',)
    save_as = True
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = StaticMenuItems.objects.filter(type=StaticMenuItems.STATIC_MENU_ITEM_TYPES_HEADER)
        return super(StaticMenuItemsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(StaticContent, StaticContentAdmin)
admin.site.register(StaticMenuItems, StaticMenuItemsAdmin)

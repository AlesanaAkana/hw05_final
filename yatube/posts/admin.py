from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_display_links = ('pk', 'text')
    list_editable = ('group',)
    search_fields = ('text', 'author')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description'
    )
    list_display_links = ('pk', 'title')
    search_fields = ('title',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'pub_date',
        'author',
    )
    list_filter = ('pub_date',)
    search_fields = ('author', 'post', 'text')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

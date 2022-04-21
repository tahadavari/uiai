from django.contrib import admin

# Register your models here.
from blog.models import Post, Tag, Bookmark, Report, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ['hash']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    exclude = ['hash']


admin.site.register([Bookmark, Report, Like, Comment])

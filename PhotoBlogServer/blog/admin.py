from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'published_date', 'updated_date')
    search_fields = ('title', 'text')
    readonly_fields = ('thumbnail', 'updated_date')

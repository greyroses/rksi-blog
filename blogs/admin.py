from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'date_added')
    list_filter = ('owner', 'date_added')
    search_fields = ('title', 'text')
    ordering = ('-date_added',)

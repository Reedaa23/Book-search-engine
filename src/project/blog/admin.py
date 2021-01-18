from django.contrib import admin
from .models import Post

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'authors', 'subjects', 'bookshelves', 'languages', 'copyright', 'content_url', 'download_count')

admin.site.register(Post, PostAdmin)

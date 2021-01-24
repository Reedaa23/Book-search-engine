from django.contrib import admin
from my_gutenberg.models import Ebook

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'authors', 'subjects', 'bookshelves', 'languages', 'copyright', 'content_url', 'cover_url', 'download_count')

admin.site.register(Ebook, PostAdmin)
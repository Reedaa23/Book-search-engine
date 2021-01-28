from django.db import models

# Create your models here.

class Ebook(models.Model):   

    id = models.IntegerField(default='-1', primary_key=True)
    title = models.CharField(max_length=200)
    release_date = models.CharField(max_length=200, blank=True, null=True, default=None)
    authors = models.TextField(max_length=500, default=None)
    subjects = models.TextField(max_length=500, blank=True, null=True, default=None)
    bookshelves = models.TextField(max_length=500, blank=True, null=True, default=None)
    languages = models.TextField(max_length=500, blank=True, null=True, default=None)
    copyright = models.TextField(max_length=500, blank=True, null=True, default=None)
    content_url = models.URLField(max_length=200, default=None)
    cover_url = models.URLField(max_length=200, blank=True, null=True, default=None)
    download_count = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True)
    neighbors = models.TextField(max_length=500, blank=True, null=True, default=None)
    keywords = models.CharField(max_length=200, blank=True, null=True, default=None)



    class Meta:
        ordering = ('id',)

    def __str__(self):
        return '%s' % self.title
from django.core.management.base import BaseCommand, CommandError
from my_gutenberg.models import Ebook
from my_gutenberg.serializers import EbookSerializer
import requests
import time
import json
from my_gutenberg.management.commands.importer import ebooks

class Command(BaseCommand):
    help = 'Refresh the list of ebooks.'

    def handle(self, *args, **options):
        self.stdout.write('['+time.ctime()+'] Refreshing data...')
        response = ebooks()
        Ebook.objects.all().delete()
        for ebook in response:
            serializer = EbookSerializer(
                data={'id':str(json.loads(ebook)['id']),
                    'title':str(json.loads(ebook)['title']),
                    'authors':str(json.loads(ebook)['authors']),
                    'subjects':str(json.loads(ebook)['subjects']),
                    'bookshelves':str(json.loads(ebook)['bookshelves']),
                    'languages':str(json.loads(ebook)['languages']),
                    'copyright':str(json.loads(ebook)['copyright']),
                    'content_url':str(json.loads(ebook)['content_url']),
                    'cover_url':str(json.loads(ebook)['cover_url']),
                    'download_count':str(json.loads(ebook)['download_count'])
                })
            if serializer.is_valid():
                serializer.save()
                self.stdout.write(self.style.SUCCESS('['+time.ctime()+'] Successfully added ebook id="%s"' % json.loads(ebook)['id']))
        self.stdout.write('['+time.ctime()+'] Data refresh terminated.')
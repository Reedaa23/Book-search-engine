from django.core.management.base import BaseCommand
from my_gutenberg.models import Ebook
from my_gutenberg.serializers import EbookSerializer
import time
from my_gutenberg.management.commands.importer import ebooks

class Command(BaseCommand):
    help = 'Initialize ebooks database'

    def handle(self, *args, **options):
        self.stdout.write('['+time.ctime()+'] Initializing ebooks database')
        response = ebooks()
        Ebook.objects.all().delete()
        for ebook in response:
            serializer = EbookSerializer(data=ebook)
            if serializer.is_valid():
                serializer.save()
                self.stdout.write(self.style.SUCCESS('['+time.ctime()+'] Successfully added ebook id="%s"' % ebook['id']))

        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')
from django.core.management.base import BaseCommand
from my_gutenberg.models import Ebook
from my_gutenberg.serializers import EbookSerializer
import time
from my_gutenberg.management.commands.importer import ebooks

class Command(BaseCommand):
    help = 'Initialize ebooks database'

    def add_arguments(self, parser):
        parser.add_argument('first_ebook', type=int, help='First ebook id to be added')
        parser.add_argument('last_ebook', type=int, help='Last ebook id to be added')

    def handle(self, *args, **kwargs):
        self.stdout.write('['+time.ctime()+'] Initializing ebooks database')

        Ebook.objects.all().delete()
        first_ebook_id = kwargs['first_ebook']
        last_ebook_id = kwargs['last_ebook']
        response = ebooks(first_ebook_id, last_ebook_id)
        
        for ebook in response:
            serializer = EbookSerializer(data=ebook)
            if serializer.is_valid():
                serializer.save()
                self.stdout.write(self.style.SUCCESS('['+time.ctime()+'] Successfully added ebook id="%s"' % ebook['id']))

        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')
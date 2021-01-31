from django.core.management.base import BaseCommand
from my_gutenberg.models import Ebook
from my_gutenberg.serializers import EbookSerializer
import time
from my_gutenberg.management.commands.importer import get_ebook
from django.contrib.admin.models import LogEntry
from collections import Counter
import re
import urllib
import numpy as np
import networkx as nx
import itertools
# from sklearn.feature_extraction.text import TfidfVectorizer

class Command(BaseCommand):
    help = 'Initialize ebooks database'

    def add_arguments(self, parser):
        parser.add_argument('first_ebook', type=int, help='First ebook id to be added')
        parser.add_argument('last_ebook', type=int, help='Last ebook id to be added')

    def handle(self, *args, **kwargs):
        self.stdout.write('['+time.ctime()+'] Initializing ebooks database')

        LogEntry.objects.all().delete()
        Ebook.objects.all().delete()

        first_ebook_id = kwargs['first_ebook']
        last_ebook_id = kwargs['last_ebook']
        
        for ebook_number in range(first_ebook_id, last_ebook_id +1):
            try:
                ebook = get_ebook(ebook_number)
                serializer = EbookSerializer(data=ebook)
                if serializer.is_valid():
                    serializer.save()
                    self.stdout.write(self.style.SUCCESS('['+time.ctime()+'] Successfully added ebook id="%s"' % ebook_number))
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('['+time.ctime()+'] Skipped ebook id="%s"' % ebook_number))

        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')
        
        
        a = Ebook.objects.values_list("content_url")
        books_urls = list(itertools.chain(*a))


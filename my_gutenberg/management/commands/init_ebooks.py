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
import json
from sklearn.feature_extraction.text import TfidfVectorizer

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


        languages = Ebook.objects.values_list("languages")
        languages = list(itertools.chain(*languages))

        a = Ebook.objects.values_list("content_url")
        books_urls = list(itertools.chain(*a))
        
        decoding = "ISO-8859-1"
        special_letters = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        
        words_list = []
        
        for i in range(len(books_urls)):

            txt = urllib.request.urlopen(books_urls[i]).read().decode(decoding)
            s1 = re.split('[^a-zA-Z0-9'+special_letters+']', txt.lower())
            str1 = list(filter(lambda x: x !="", s1))
            words_list.append(str1) 

            if languages[i] == "en":
                vectorizer = TfidfVectorizer(max_features = 10, lowercase=False, stop_words = 'english')
            else:
                vectorizer = TfidfVectorizer(max_features = 10, lowercase=False, stop_words = safe_get_stop_words(languages[i]))

            X = vectorizer.fit_transform(words_list[i])
            keywords = list(vectorizer.vocabulary_.keys())
            kw = ','.join(keywords)
            e = Ebook.objects.get(content_url = books_urls[i])
            e.keywords = kw
            e.save()
            with open('str.json','w', encoding='utf-8') as str_file:
                json.dump(words_list, str_file, ensure_ascii=False, indent=4)
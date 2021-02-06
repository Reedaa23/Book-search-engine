from django.core.management.base import BaseCommand
import time
from my_gutenberg.management.commands.importer import get_ebook
import requests
import json
import os

ES_URL = "http://" + os.getenv('ES_host', 'localhost') +":9200/"

class Command(BaseCommand):
    help = 'Fill completion field'

    def add_arguments(self, parser):
        parser.add_argument('first_ebook', type=int, help='First ebook id to be added')
        parser.add_argument('last_ebook', type=int, help='Last ebook id to be added')

        
    def handle(self, *args, **kwargs):
        self.stdout.write('['+time.ctime()+'] Adding title_suggest mapping')

        first_ebook_id = kwargs['first_ebook']
        last_ebook_id = kwargs['last_ebook']

        r = requests.put(ES_URL + "ebooks/_mapping",headers={'Content-type':'application/json'} ,data={"properties": {"title_suggest": {"type": "completion"}}})
        for i in range(first_ebook_id, last_ebook_id + 1):
            try:
                ebook = get_ebook(i)
                title_list = ebook['title'].split(" ")
                input = [ebook['title']]
                length = len(title_list)
                for i in range(1,length):
                    s = slice(i,length,1)
                    input.append(' '.join(title_list[s]))
                r = requests.post(ES_URL+"ebooks/_update/"+str(ebook['id']), headers={'Content-type':'application/json'} ,data=json.dumps({"doc":{"title_suggest": {"input": input}}}))
                self.stdout.write('['+time.ctime()+'] Completion setup for ebook ' + str(ebook['id']))
            except FileNotFoundError:
                continue


        self.stdout.write('['+time.ctime()+'] Completion setup finished.')

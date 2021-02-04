from django.core.management.base import BaseCommand
import time
from my_gutenberg.management.commands.importer import get_ebook
import requests
import json

ES_URL = "http://localhost:9200/"

class Command(BaseCommand):
    help = 'Fill completion field'

        
    def handle(self, *args, **kwargs):
        self.stdout.write('['+time.ctime()+'] Adding title_suggest mapping')
        #r = requests.put(ES_URL + "ebooks/_mapping",headers={} ,data={"properties": {"title_suggest": {"type": "completion"}}})
        #print(r.text)
        self.stdout.write('['+time.ctime()+'] Filling title_suggest field')
        for i in range(62350, 64151):
            try:
                ebook = get_ebook(i)
                title_list = ebook['title'].split(" ")
                input = [ebook['title']]
                length = len(title_list)
                for i in range(1,length):
                    s = slice(i,length,1)
                    input.append(' '.join(title_list[s]))
                    print(title_list[s])
                r = requests.post(ES_URL+"ebooks/_update/"+str(ebook['id']), headers={'Content-type':'application/json'} ,data=json.dumps({"doc":{"title_suggest": {"input": input}}}))
                print(r.text)
            except FileNotFoundError:
                continue


        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')

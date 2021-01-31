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
import os.path
from os import path
from pandas import DataFrame
import json
from networkx.readwrite import json_graph

class Command(BaseCommand):
    help = 'Fill jaccard matrix'



    def add_arguments(self, parser):
        parser.add_argument('first_ebook', type=int, help='First ebook id to be added')
        parser.add_argument('last_ebook', type=int, help='Last ebook id to be added')

    def handle(self, *args, **kwargs):
        self.stdout.write('['+time.ctime()+'] Filling Jaccard matrix')

        # LogEntry.objects.all().delete()
        # Ebook.objects.all().delete()

        first_ebook_id = kwargs['first_ebook']
        last_ebook_id = kwargs['last_ebook']
        
        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')
        
        books_urls = []
        for ebook_number in range(first_ebook_id, last_ebook_id +1):
            try:
                url = get_ebook(ebook_number)['content_url']
                books_urls.append(url)
            except FileNotFoundError:
                continue
            

        decoding = "ISO-8859-1"
        special_letters = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        n = len(books_urls)
        jaccard_file_name = './matrix.json'
        threshold = 0.7
        
        if os.path.isfile(jaccard_file_name):
            print ("File exist")
            f = open(jaccard_file_name, 'r')
            MATRIX = json.load(f)
            f.close()

            file_str = open('str.json', 'r')
            str_list = json.load(file_str)
            file_str.close()

            file_line = open("lastLine.json", 'r')
            next_line = json.load(file_line) + 1
            file_line.close()

            file_graph = open("graph.json", "r")
            g_data = json.load(file_graph)
            file_graph.close()
            G = json_graph.node_link_graph(g_data)
            print(G.nodes())



        else:
            print ("File not exist")
            MATRIX = np.zeros((n, n))
            next_line = 0
            str_list = []
            G = nx.Graph()
        
        print('initial matrix')
        print(DataFrame(MATRIX))
        print('['+time.ctime()+'] Calculating Jaccard Matrix...')


        for i in range(next_line,len(books_urls)):
            print(i)

            if i ==0:
                txt = urllib.request.urlopen(books_urls[i]).read().decode(decoding)
                print(books_urls[i])
                s1 = re.split('[^a-zA-Z0-9'+special_letters+']', txt.lower())
                str1 = list(filter(lambda x: x !="", s1))
                str_list.append(str1)
            else:
                str1 = str_list[i]

            for j in range(len(books_urls))[i + 1:]:
                print("    ",books_urls[j])
                num = 0
                denom = 0

                if i==0:
                    txt2 = urllib.request.urlopen(books_urls[j]).read().decode(decoding)
                    s2 = re.split('[^a-zA-Z0-9'+special_letters+']', txt2.lower())
                    str2 = list(filter(lambda x: x !="", s2))
                    str_list.append(str2)
                    with open('str.json','w', encoding='utf-8') as str_file:
                        json.dump(str_list, str_file, ensure_ascii=False, indent=4)
                else:
                    str2 = str_list[j]

                D = str1 + str2
                d1 = Counter(str1)
                d2 = Counter(str2)

                for m in D:
                    k1 = d1[m]
                    k2 = d2[m]
                    MAX = max(k1, k2)
                    MIN = min(k1, k2)
                    num = num + MAX - MIN
                    denom = denom + MAX
                MATRIX[i][j] = num / denom
                
                distance = MATRIX[i][j]
                if distance < threshold:
                    G.add_edge(books_urls[i], books_urls[j], weight = distance)
                with open('graph.json','w', encoding='utf-8') as fg:
                    g_json = json_graph.node_link_data(G)
                    json.dump(g_json,fg,indent=4)

            CC = nx.closeness_centrality(G)
            ranking = sorted(CC.items(), key=lambda item: item[1], reverse=True)
            print(ranking)
            for tup in ranking:
                url = tup[0]
                print("url : ", url)
                rank = ranking.index(tup) + 1
                e = Ebook.objects.get(content_url = url)
                e.rank = rank
                e.save()

      
            # Finished a line ? write in the file
            try:
                matrix = MATRIX.tolist()
            except AttributeError:
                matrix = MATRIX 
            with open('matrix.json','w', encoding='utf-8') as f:
                json.dump(matrix, f, ensure_ascii=False, indent=4)
            with open('lastLine.json', 'w', encoding='utf-8') as ff:
                json.dump(i, ff, ensure_ascii=False, indent=4)

        print('['+time.ctime()+'] Calculating Jaccard Matrix terminated...')
        print(DataFrame(MATRIX))
        print(G.edges())
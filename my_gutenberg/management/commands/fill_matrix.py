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

        first_ebook_id = kwargs['first_ebook']
        last_ebook_id = kwargs['last_ebook']
        
        self.stdout.write('['+time.ctime()+'] Database initializing terminated.')
        

        books_urls = []


        a = Ebook.objects.filter(id__range=[first_ebook_id, last_ebook_id]).values_list("content_url")
        books_urls = list(itertools.chain(*a))
        languages = Ebook.objects.values_list("languages")
        languages = list(itertools.chain(*languages))


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
        else:
            print ("File not exist")
            print("Please run init_ebooks first")
            MATRIX = np.zeros((n, n))


        
        lastLine_file_name = "./lastLine.json"
        if os.path.isfile(lastLine_file_name):
            file_line = open(lastLine_file_name, 'r')
            next_line = json.load(file_line)
            file_line.close()
        else:
            next_line = 0




        graph_file_name = "./graph.json"
        if os.path.isfile(graph_file_name):
            file_graph = open("graph.json", "r")
            g_data = json.load(file_graph)
            file_graph.close()
            G = json_graph.node_link_graph(g_data)
        else:
            G = nx.Graph()




        words_file_name = './str.json'
        if os.path.isfile(words_file_name):
            file_str = open(words_file_name, 'r')
            str_list = json.load(file_str)
            file_str.close()
        else:
            exit()





        print('initial matrix')
        print(DataFrame(MATRIX))
        print('['+time.ctime()+'] Calculating Jaccard Matrix...')


        for i in range(next_line,len(books_urls)):
            try:
                str1 = str_list[i]
                print("Row number : {} ".format(i))
            except IndexError:
                exit()
                

            for j in range(len(books_urls))[i + 1:]:
                num = 0
                denom = 0
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
            for tup in ranking:
                url = tup[0]
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
            with open(lastLine_file_name, 'w', encoding='utf-8') as ff:
                json.dump(i, ff, ensure_ascii=False, indent=4)
        


            for node in G.nodes:
                voisins = G.neighbors(node)
                neighbors = ""
                for voisin in voisins:
                    m = re.search('http://www.gutenberg.org/files/([0-9]+)/', voisin)
                    if m:
                        id = m.group(1)
                        neighbors += id + "/"
                    else:
                        continue

                e = Ebook.objects.get(content_url=node)
                e.neighbors = neighbors
                e.save()


        print('['+time.ctime()+'] Calculating Jaccard Matrix terminated...')
        print(DataFrame(MATRIX))
        os.remove(words_file_name)
        os.remove(lastLine_file_name)
        os.remove(graph_file_name)

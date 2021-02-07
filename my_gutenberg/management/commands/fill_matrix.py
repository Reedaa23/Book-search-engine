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
import ssl
from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import safe_get_stop_words

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
        
        # Recuperation des valeurs des champs content_url correspondants aux id
        books_urls = []
        a = Ebook.objects.filter(id__range=[first_ebook_id, last_ebook_id]).values_list("content_url")
        books_urls = list(itertools.chain(*a))

        # Recuperation des valeurs des champs languages correspondants aux id
        languages = Ebook.objects.filter(id__range=[first_ebook_id, last_ebook_id]).values_list("languages")
        languages = list(itertools.chain(*languages))

        # Contexte pour pouvoir lire les urls en https
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        n = len(books_urls)

        # Initialisation de la matrice N x N
        MATRIX = np.zeros((n, n))

        # Decodeur de caractères
        decoding = "ISO-8859-1"

        # Caractères speciaux pour le decoupage de mots
        special_letters = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        
        # Initialisation du graphe
        G = nx.Graph()

        # Seuil en dessous duquel il existe un lien entre deux noeuds
        threshold = 0.7
        str_list = []


        # Remplissage de la matrice ligne par ligne
        # Lire le contenu de l'url, decoupage du texte en liste mots, stocker cette liste pour lire directement pour les autres lignes
        # D : union des mots des deux ebooks
        # d1, d2 : retourne un dict {mot : nombre d'occurence}
        # Calculer la distance et assigner la valeur
        # Ajouter un lien entre les deux noeuds si la distance < au seuil
        # Extraire les keywords avec scikit learn
        # Affecter ces keywords aux objets Django correspondants

        for i in range(len(books_urls)):
            print("Row number : ", i)
            if i ==0:
                txt = urllib.request.urlopen(books_urls[i], context = ctx).read().decode(decoding)
                s1 = re.split('[^a-zA-Z0-9'+special_letters+']', txt.lower())
                str1 = list(filter(lambda x: x !="", s1))
                str_list.append(str1)
            else:
                str1 = str_list[i]

            for j in range(len(books_urls))[i + 1:]:
                print("Column number : ", j)
                num = 0
                denom = 0
                if i==0:
                    txt2 = urllib.request.urlopen(books_urls[j], context = ctx).read().decode(decoding)
                    s2 = re.split('[^a-zA-Z0-9'+special_letters+']', txt2.lower())
                    str2 = list(filter(lambda x: x !="", s2))
                    str_list.append(str2)
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
            

            if languages[i] == "en":
                vectorizer = TfidfVectorizer(max_features = 10, lowercase=False, stop_words = 'english')
            else:
                vectorizer = TfidfVectorizer(max_features = 10, lowercase=False, stop_words = safe_get_stop_words(languages[i]))

            X = vectorizer.fit_transform(str_list[i])
            keywords = list(vectorizer.vocabulary_.keys())
            kw = ','.join(keywords)
            e = Ebook.objects.get(content_url = books_urls[i])
            e.keywords = kw
            e.save()

        try:
            matrix = MATRIX.tolist()
        except AttributeError:
            matrix = MATRIX 
        with open('matrix.json','w', encoding='utf-8') as f:
            json.dump(matrix, f, ensure_ascii=False, indent=4)

        self.stdout.write('['+time.ctime()+']  Jaccard Matrix calculated...')
        self.stdout.write('['+time.ctime()+'] Graph generated...')
    
        # Closeness centrality, return {"vetex" : cc, "vertex" : cc }
        self.stdout.write('['+time.ctime()+'] Calculating CC...')
        CC = nx.closeness_centrality(G)
        self.stdout.write('['+time.ctime()+']  CC calculated...')
        
        # Ranking
        self.stdout.write('['+time.ctime()+'] Calculating ranking...')
        ranking = sorted(CC.items(), key=lambda item: item[1], reverse=True)

        for tup in ranking:
            url = tup[0]
            rank = ranking.index(tup) + 1
            e = Ebook.objects.get(content_url = url)
            e.rank = rank
            e.save()

        self.stdout.write('['+time.ctime()+']  Ranking calculated...')

        self.stdout.write('['+time.ctime()+']  Calculating neighbors...')


        for node in G.nodes:
            voisins = G.neighbors(node)
            neighbors = ""
            for voisin in voisins:
                m = re.search('www.gutenberg.org/files/([0-9]+)/', voisin)
                if m:
                    id = m.group(1)
                    neighbors += id + "/"
                else:
                    continue

            e = Ebook.objects.get(content_url=node)
            e.neighbors = neighbors
            e.save()


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
from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import safe_get_stop_words

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
        languages = Ebook.objects.values_list("languages")
        languages = list(itertools.chain(*languages))

        self.stdout.write('['+time.ctime()+'] Calculating Jaccard Matrix and Graph...')
        txt_list = []
        str_list = []
        special_letters = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        decoding = "ISO-8859-1"
        n = len(books_urls)
        MATRIX = np.zeros((n, n))
        # Graph 
        threshold = 0.7
        G = nx.Graph()
        

        # Remplissage ligne par ligne
        for i in range(len(books_urls)):

            # Si premier ebook, faire le décodage, sinon utiliser le texte déja décodé 
            if i ==0:
                # Ouvir l'url, lire puis décoder le contenu
                txt = urllib.request.urlopen(books_urls[i]).read().decode(decoding)
                txt_list.append(txt)
                # Ajouter le texte décodé dans la liste des textes 
                print(books_urls[i])
                # Rendre le texte en minuscule, diviser en mots, mettre ces mots dans une liste
                s1 = re.split('[^a-zA-Z0-9'+special_letters+']', txt.lower())
                str1 = list(filter(lambda x: x !="", s1))
                str_list.append(str1)
            else:
                str1 = str_list[i]


            for j in range(len(books_urls))[i + 1:]:

                print("    ",books_urls[j])
                num = 0
                denom = 0
                # Si premier livre, décoder et ajouter le texte décodé des autres livres, sinon  
                if i==0:
                    txt2 = urllib.request.urlopen(books_urls[j]).read().decode(decoding)
                    s2 = re.split('[^a-zA-Z0-9'+special_letters+']', txt2.lower())
                    str2 = list(filter(lambda x: x !="", s2))
                    str_list.append(str2)
                    txt_list.append(txt2)
                else:
                    str2 = str_list[j]


                # Fusionner les deux listes de mots 
                D = str1 + str2
                # d1 et d2 : nombre d'occurence de chaque mot dans le livre1 et livre2
                d1 = Counter(str1)
                d2 = Counter(str2)

                # Pour chaque mot dans les deux livres, récuperer son nombre d'occurence
                # print( '['+time.ctime()+'] commence comptage')
                for m in D:
                    k1 = d1[m]
                    k2 = d2[m]
                    MAX = max(k1, k2)
                    MIN = min(k1, k2)
                    num = num + MAX - MIN
                    denom = denom + MAX
                MATRIX[i][j] = num / denom
                # print('['+time.ctime()+']fini comptage')

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
                m = re.search('http://www.gutenberg.org/files/([0-9]+)/', voisin)
                if m:
                    id = m.group(1)
                    neighbors += "/"+id
                else:
                    continue

            e = Ebook.objects.get(content_url=node)
            e.neighbors = neighbors
            e.save()
            
        self.stdout.write('['+time.ctime()+'] END...')
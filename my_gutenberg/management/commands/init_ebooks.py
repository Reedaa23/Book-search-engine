from django.core.management.base import BaseCommand
from my_gutenberg.models import Ebook
from my_gutenberg.serializers import EbookSerializer
import time
from my_gutenberg.management.commands.importer import get_ebook

from collections import Counter
import re
import urllib
import numpy as np
import networkx as nx

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


        self.stdout.write('['+time.ctime()+'] Calculating Jaccard Matrix...')
        txt_list = []
        special_letters = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'
        decoding = "ISO-8859-1"
        n = len(books_urls)
        MATRIX = np.zeros((n, n))

        # Remplissage ligne par ligne
        for i in range(len(books_urls)):

            # Si premier ebook, faire le décodage, sinon utiliser le texte déja décodé 
            if i ==0:
                # Ouvir l'url, lire puis décoder le contenu
                txt = urllib.request.urlopen(books_urls[i]).read().decode(decoding)
                # Ajouter le texte décodé dans la liste des textes 
                txt_list.append(txt)
            else:
                txt = txt_list[i]

            # Rendre le texte en minuscule, diviser en mots, mettre ces mots dans une liste
            s1 = re.split('[^a-zA-Z0-9'+special_letters+']', txt.lower())
            str1 = list(filter(lambda x: x !="", s1))
            
            for j in range(len(books_urls))[i + 1:]:
                num = 0
                denom = 0
                # Si premier livre, décoder et ajouter le texte décodé des autres livres, sinon  
                if i==0:
                    txt2 = urllib.request.urlopen(books_urls[j]).read().decode(decoding)
                    txt_list.append(txt2)
                else:
                    txt2 = txt_list[j]

                s2 = re.split('[^a-zA-Z0-9'+special_letters+']', txt2.lower())
                str2 = list(filter(lambda x: x !="", s2))

                # Fusionner les deux listes de mots 
                D = str1 + str2
                # d1 et d2 : nombre d'occurence de chaque mot dans le livre1 et livre2
                d1 = Counter(str1)
                d2 = Counter(str2)

                # Pour chaque mot dans les deux livres, récuperer son nombre d'occurence
                for m in D:
                    k1 = d1[m]
                    k2 = d2[m]
                    MAX = max(k1, k2)
                    MIN = min(k1, k2)
                    num = num + MAX - MIN
                    denom = denom + MAX
                MATRIX[i][j] = num / denom

        self.stdout.write('['+time.ctime()+']  Jaccard Matrix calculated...')
         
        # Graph 
        self.stdout.write('['+time.ctime()+'] Calculating Graph...')
        threshold = 0.7
        G = nx.Graph()

        for i in range(len(books_urls)):
            for j in range(len(books_urls))[i+1:]:
                distance = MATRIX[i][j]
                if distance < threshold:
                    G.add_edge(books_urls[i], books_urls[j], weight = distance)
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
            e.classement = rank
            e.save()

        self.stdout.write('['+time.ctime()+']  Ranking calculated...')



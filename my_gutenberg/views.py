from copy import Error
from django.http import Http404, HttpResponseServerError
from my_gutenberg.documents import PostDocument
from rest_framework.views import APIView
from rest_framework.response import Response
from my_gutenberg.models import Ebook
from .serializers import EbookSerializer
import random

# Create a view that returns all the ebooks with all their fields
class AllEbooks(APIView):

    def get(self, request, format=None):
        try:
            ebooks = Ebook.objects.all()
            serializer = EbookSerializer(ebooks, many=True)
            return Response(serializer.data)
        except:
            raise HttpResponseServerError


# Create a view that returns 8 random ebooks with all their fields
class RandomEbooks(APIView):
    def get(self, request, format=None):
        try:
            all_ebooks = list(Ebook.objects.all())
            # In case we have less than 8 ebooks in our database
            if len(all_ebooks) < 8:
                randomlist = random.sample(list(Ebook.objects.all()),len(all_ebooks))
            else:
                randomlist = random.sample(list(Ebook.objects.all()),8)
            response = []
            for ebook in randomlist:
                serializer = EbookSerializer(ebook, many=False)
                response.append(serializer.data)
            return Response(response)
        except:
            raise HttpResponseServerError


# Create a view that returns all fields of an ebook with the given id
class EbookDetail(APIView):
    
    def get(self, request, pk, format=None):
        try:
            ebook = Ebook.objects.get(id=pk)
            serializer = EbookSerializer(ebook, many=False)
            return Response(serializer.data)
        except:
            raise HttpResponseServerError

# Create a view that performs simple and advanced search
class Search(APIView):
    def get(self, request, format=None):   
        try:
            key = request.query_params.get('key')
            regex = request.query_params.get('regex', 'false')
            
            if(regex.lower() == 'true'):
                # Advanced search
                es_request = PostDocument.search().query('query_string', query=key).highlight('title','authors', pre_tags="<mark>", post_tags="</mark>")
            else:
                # Simple search
                es_request = PostDocument.search().query('multi_match', query=key, fields=["title", "authors", "subjects", "bookshelves", "keywords"], type="phrase").highlight('title','authors', pre_tags="<mark>", post_tags="</mark>")
            
            es_response = es_request.execute()
            response = {'result': [], 'neighbors': [] }
            suggested_neighbors = []
            for book in es_response.to_dict()['hits']['hits']:
                # Highlight
                book_source = book['_source']
                if(book.get('highlight', None)):
                    if(book['highlight'].get('title', None)):
                        book_source['title'] = book['highlight']['title'][0]
                if(book.get('highlight', None)):
                    if(book['highlight'].get('authors', None)):
                        book_source['authors'] = book['highlight']['authors'][0]
                response['result'].append(book_source)
                if 'neighbors' in book['_source'].keys():
                    neighbors = book['_source']['neighbors'].split('/')
                    if (len(suggested_neighbors) < 5):
                        for neighbor in neighbors:
                            # Add neighbors of the first ebook of the search's result
                            if neighbor not in suggested_neighbors and neighbor != "":
                                suggested_neighbors.append(neighbor)
                                # When 5 ebooks are suggested, we stop
                                if (len(suggested_neighbors) == 5):
                                    break
            # Return id, title and authors of the suggested ebooks                        
            for neighbor in suggested_neighbors:
                ebook = Ebook.objects.get(id=neighbor)
                serializer = EbookSerializer(ebook, many=False)
                response['neighbors'].append({"id": serializer.data["id"], "title": serializer.data["title"], "authors": serializer.data["authors"]})
            return Response(response)
        except :
            raise HttpResponseServerError

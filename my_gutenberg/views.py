from django.http import Http404
from my_gutenberg.documents import PostDocument
from rest_framework.views import APIView
from rest_framework.response import Response
from my_gutenberg.models import Ebook
from .serializers import EbookSerializer
import random

# Create your views here.

class AllEbooks(APIView):

    def get(self, request, format=None):
        ebooks = Ebook.objects.all()
        serializer = EbookSerializer(ebooks, many=True)
        return Response(serializer.data)
#    def post(self, request, format=None):
#        NO DEFITION of post --> server will return "405 NOT ALLOWED"

class RandomEbooks(APIView):

    def get(self, request, format=None):

        randomlist = random.sample(list(Ebook.objects.all()),8)
        response = []
        for ebook in randomlist:
            serializer = EbookSerializer(ebook, many=False)
            response.append(serializer.data)
        return Response(response)
#    def post(self, request, format=None):
#        NO DEFITION of post --> server will return "405 NOT ALLOWED"

class EbookDetail(APIView):
    
    def get(self, request, pk, format=None):
        ebook = Ebook.objects.get(id=pk)
        serializer = EbookSerializer(ebook, many=False)
        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"

class Search(APIView):
    def get(self, request, format=None):
        fields = [
            'id', 'title', 'authors', 'subjects', 'bookshelves', 'languages', 'copyright', 'content_url', 'cover_url', 'download_count', 'release_date','rank', 'neighbors','keywords'
        ]
        #try:
        key = request.query_params.get('key')
        regex = request.query_params.get('regex', 'false')
        
        if(regex.lower() == 'true'):
            es_request = PostDocument.search().query('query_string', query=key)
        else:
            es_request = PostDocument.search().query('multi_match', query=key, fields=["title", "authors", "subjects", "bookshelves", "keywords"], type="phrase")
        
        es_response = es_request.execute()
        response = {'result': [], 'neighbors': [] }
        suggested_neighbors = []
        for book in es_response.to_dict()['hits']['hits']:
            response['result'].append(book['_source'])
            if 'neighbors' in book['_source'].keys():
                neighbors = book['_source']['neighbors'].split('/')
                if (len(suggested_neighbors) < 5):
                    for neighbor in neighbors:
                        if neighbor not in suggested_neighbors:
                            suggested_neighbors.append(neighbor)
                            if (len(suggested_neighbors) == 5):
                                break
        for neighbor in suggested_neighbors:
            ebook = Ebook.objects.get(id=neighbor)
            serializer = EbookSerializer(ebook, many=False)
            response['neighbors'].append({"title": serializer.data["title"], "authors": serializer.data["authors"]})
        return Response(response)
        """except:
            raise Http404"""
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"
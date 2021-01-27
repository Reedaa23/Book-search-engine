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
        try:
            key = request.query_params.get('key')
            regex = request.query_params.get('regex', 'false')
            
            if(regex.lower() == 'true'):
                es_request = PostDocument.search().query('query_string', query=key)
            else:
                es_request = PostDocument.search().query('match', title=key)
            
            es_response = es_request.execute()
            response = []
            for book in es_response.to_dict()['hits']['hits']:
                response.append(book['_source'])
            return Response(response)
        except:
            raise Http404
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"
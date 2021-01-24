from django.shortcuts import render
from my_gutenberg.documents import PostDocument
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core import serializers
from my_gutenberg.models import Ebook
import json
import random

# Create your views here.

class EbooksRedirection(APIView):

    def get(self, request, format=None):
        response = Ebook.objects.all()
        data = serializers.serialize('json', response)
        data = json.loads(data)
        return Response(data)
#    def post(self, request, format=None):
#        NO DEFITION of post --> server will return "405 NOT ALLOWED"

class RandomEbooksRedirection(APIView):

    def get(self, request, format=None):
        response = random.sample(list(Ebook.objects.all()), 8)
        data = serializers.serialize('json', response)
        data = json.loads(data)
        return Response(data)
#    def post(self, request, format=None):
#        NO DEFITION of post --> server will return "405 NOT ALLOWED"

class EbookDetailRedirection(APIView):

    def get_object(self, pk):
        try:
            response = Ebook.objects.filter(pk=pk)
            data = serializers.serialize('json', response)
            data = json.loads(data)
            return Response(data)
        except:
            raise Http404

    def get(self, request, pk, format=None):
        response = Ebook.objects.filter(pk=pk)
        data = serializers.serialize('json', response)
        data = json.loads(data)
        return Response(data)
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"

class SimpleSearchRedirection(APIView):

    def get_object(self, str):
        try:
            response = PostDocument.search().query('match', title=str)
            response = response.execute()
            return Response(response.to_dict())
        except:
            raise Http404

    def get(self, request, str, format=None):
        response = PostDocument.search().query('match', title=str)
        response = response.execute()
        return Response(response.to_dict())
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"

class AdvancedSearchRedirection(APIView):

    def get_object(self, str):
        try:
            response = PostDocument.search().query('query_string', query=str)
            response = response.execute()
            return Response(response.to_dict())
        except:
            raise Http404

    def get(self, request, str, format=None):
        response = PostDocument.search().query('query_string', query=str)
        response = response.execute()
        return Response(response.to_dict())
#    def put(self, request, pk, format=None):
#        NO DEFITION of put --> server will return "405 NOT ALLOWED"
#    def delete(self, request, pk, format=None):
#        NO DEFITION of delete --> server will return "405 NOT ALLOWED"

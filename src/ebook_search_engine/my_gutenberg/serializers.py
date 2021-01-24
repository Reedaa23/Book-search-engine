from rest_framework.serializers import ModelSerializer
from my_gutenberg.models import Ebook

class EbookSerializer(ModelSerializer):
    class Meta:
        model = Ebook
        fields = ('id', 'title', 'authors', 'subjects', 'bookshelves', 'languages', 'copyright', 'content_url', 'cover_url', 'download_count')
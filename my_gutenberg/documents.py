from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from my_gutenberg import models

# Index in Elasticsearch
@registry.register_document
class PostDocument(Document):      
    
    class Index:        
        name = 'ebooks'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = models.Ebook
        fields = [
            'id', 'title', 'authors', 'subjects', 'bookshelves', 'languages', 'copyright', 'content_url', 'cover_url', 'download_count', 'release_date','rank', 'neighbors','keywords'
        ]
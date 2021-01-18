from django.shortcuts import render
from .documents import PostDocument

# Create your views here.

def search(request):

    search_type = request.GET.get('search_type')
    search_query = request.GET.get('search_query')
    if search_type == "simple" and search_query:
        posts = PostDocument.search().query('match', title=search_query)
    elif search_type == "regex" and search_query:
        posts = PostDocument.search().query('query_string', query=search_query)
    else:
        posts = ''
    
    return render(request, 'search/search.html', {'posts': posts})
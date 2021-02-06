from django.urls import path
from my_gutenberg import views

# Create paths for our application
urlpatterns = [
    path('ebooks/', views.AllEbooks.as_view()),
    path('', views.RandomEbooks.as_view()),
    path('ebook/<int:pk>/', views.EbookDetail.as_view()),
    path('search/', views.Search.as_view()),
]

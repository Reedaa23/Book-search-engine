from django.urls import path
from my_gutenberg import views

urlpatterns = [
    path('ebooks/', views.EbooksRedirection.as_view()),
    path('', views.RandomEbooksRedirection.as_view()),
    path('ebook/<int:pk>/', views.EbookDetailRedirection.as_view()),
    path('simple_search/<str:str>/', views.SimpleSearchRedirection.as_view()),
    path('advanced_search/<str:str>/', views.AdvancedSearchRedirection.as_view()),
]

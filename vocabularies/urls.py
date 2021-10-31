from django.urls import path, include

from vocabularies.views import *

urlpatterns = [
    path('search/', SearchingApi.as_view(), name='search'),
    path('sentences/', SentencesApi.as_view(), name='sentences'),
]
from django.urls import path, include

from vocabularies.views import SearchingApi

urlpatterns = [
    path('search/', SearchingApi.as_view(), name='search')
]
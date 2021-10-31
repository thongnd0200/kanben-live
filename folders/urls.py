from django.urls import path
from folders.views import *


urlpatterns = [
    path('folder/', FolderAPI.as_view()),
    path('folder/<str:id>', FolderDetailApi.as_view()),
]
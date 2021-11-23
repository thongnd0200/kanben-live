from django.urls import path
from folders.views import *


urlpatterns = [
    path('folder/', FolderAPI.as_view()),
    path('folder/<str:id>', FolderDetailApi.as_view()),
    path('listFolder/<str:id>', OwnFolderAPI.as_view()),
    path('listFolder/', ListFolderAPI.as_view()),
    path('listTopic/', TopicAPI.as_view()),
    path('listTopic/<str:id>', DeleteTopicAPI.as_view()),
]
from django.shortcuts import render
from rest_framework import status
from rest_framework.utils import serializer_helpers
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
from utils.make_response import *
from vocabularies.serializers import SearchingSerializer

# Create your views here.

class SearchingApi(APIView):
    serializer_class = SearchingSerializer

    def get(self, request):
        try:
            keyWord = request.GET.get('keyWord', '')
            print(keyWord)

            url = "https://jisho.org/api/v1/search/words?keyword=" + keyWord

            payload = ""
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.text
            parsed = json.loads(data)

            return Response(data=parsed, status=status.HTTP_200_OK)
        except Exception:
            return response_bad_request({"Key Word": "Word is not found"})    
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
from accounts.decorators import login_required
from utils.make_response import *
from vocabularies.serializers import *

# Create your views here.


class SearchingApi(generics.GenericAPIView):
    serializer_class = VocabularySerializer

    def get(self, request):
        try:
            keyWord = request.GET.get('keyWord', '')
            print(keyWord)

            url = "https://jisho.org/api/v1/search/words?keyword=" + keyWord

            payload = ""
            headers = {}
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            data = response.text
            parsed = json.loads(data)

            return Response(data=parsed, status=status.HTTP_200_OK)
        except Exception:
            return response_bad_request({"Key Word": "Word is not found"})

    @login_required
    def post(self, request):
        
        data = request.data
        print(data)
        vocabulary = data.get('vocabulary', '')
        folder = data.get('folders', '')
        if vocabulary != '' and folder != '':
            if Vocabularies.objects.filter(folders=folder, vocabulary=vocabulary).exists():
                return response_bad_request({"vocabulary": "This vocabulary already exists in this folder"})
        # definitions = json.loads(data.get('definitions'))
        # reading = json.loads(data.get('reading'))
        definitions = data.get('definitions')
        reading = data.get('reading')
        serializer = self.serializer_class(
            data={'vocabulary': vocabulary, 'definitions': definitions, 'reading': reading, 'folders': data['folders']})
        
        if serializer.is_valid() == True:
            if folder == '':
                return response_bad_request({"folder": "folder can't be blanked"})
            if vocabulary == '':
                return response_bad_request({"vocabulary": "vocabulary can't be blanked"})
            if definitions == '':
                return response_bad_request({"definitions": "definitions can't be blanked"})
            if reading == '':
                return response_bad_request({"reading": "reading can't be blanked"})
            serializer.save()
            return response_ok(serializer.data)
        else:
            print(serializer.errors)
        


class SentencesApi(APIView):
    serializer_class = VocabularySerializer

    def get(self, request):
        try:
            keyWord = request.GET.get('keyWord', '')
            print(keyWord)

            url = "https://tatoeba.org/vi/api_v0/search?from=jpn&to=jpn&query=" + keyWord

            payload = ""
            headers = {}
            response = requests.request(
                "GET", url, headers=headers, data=payload)
            data = response.text
            parsed = json.loads(data)

            return Response(data=parsed, status=status.HTTP_200_OK)
        except Exception:
            return response_bad_request({"Key Word": "Word is not found"})
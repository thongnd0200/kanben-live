from rest_framework import generics
from accounts.decorators import login_required, admin_required
from folders.serializers import *
from utils.make_response import *

# Create your views here.

class FolderAPI(generics.GenericAPIView):
    serializer_class = FolderSerializer

    @login_required
    def get(self, request):
        try:
            user = request.user
            folders = Folders.objects.filter(user=user)
            data = FolderSerializer(folders, many=True).data
            return response_ok(data)
        except Exception:
            return response_bad_request({'User': 'Unauthenticated'})

    @login_required
    def post(self, request):
        try:
            data = request.data
            serializer = self.serializer_class(
                data=data, context={'request': request})

            if serializer.is_valid() == True:
                name = data.get('name', '')
                
                if Folders.objects.filter(user=request.user, name=name).exists():
                    return response_bad_request({"name": "This folder's name already exists!"})
                if name == "":
                    return response_bad_request({"name": "This field cannot be blank."})
                serializer.save()
                return response_ok(serializer.data)

            else:
                return response_bad_request({"entered_data": "Entered data is invalid."})
        except Exception:
            return response_bad_request("Request denied.")


class FolderDetailApi(generics.GenericAPIView):
    serializer_class = FolderDetailSerializer

    @login_required
    def put(self, request, id):
        try:
            data = request.data
            folder = Folders.objects.get(id=id)
            name = data.get('name', '')
            topic = data.get('topic', '')
            visibility = data.get('visibility', '')

            serializer = self.serializer_class(data={'name': name, 'topic': topic, 'visibility': visibility})
            if serializer.is_valid() == True:
                if name == '':
                    return response_bad_request({"folder_name": "folder_name can't be blanked"})
                if topic == '':
                    return response_bad_request({"topic": "topic can't be blanked"})
                folder.name = name
                folder.topic = Topic.objects.get(id=topic)
                folder.visibility = visibility
                folder.save()
                return response_ok(FolderDetailSerializer(folder, context=self.get_serializer_context()).data)
            else:
                return response_bad_request({"entered_data": "Entered data is invalid."})

        except Folders.DoesNotExist:
            return response_not_found("Folder does not exist.")

    def get(self, request, id):
        try:
            folder = Folders.objects.get(id=id)
            data = FolderDetailSerializer(folder).data
            return response_ok(data)

        except Folders.DoesNotExist:
            return response_not_found("Folder does not exist.")

    @login_required    
    def delete(self, request, id):
        try:
            folder = Folders.objects.get(id=id)
            folder.delete()
            return response_no_content("Delete successfully.")

        except Folders.DoesNotExist:
            return response_not_found("Folder does not exist.")


class OwnFolderAPI(generics.GenericAPIView):
    serialiser_class = FolderSerializer

    @login_required
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            folder_list = Folders.objects.filter(user__id=id, visibility=True)
            data = FolderSerializer(folder_list, many=True).data
            return response_ok(data)
        except Exception:
            return response_bad_request("User does not exist.")


class ListFolderAPI(generics.GenericAPIView):
    serialiser_class = FolderSerializer

    def get(self, request):
        try:
            folder_list = Folders.objects.filter(visibility=True)
            data = FolderSerializer(folder_list, many=True).data
            return response_ok(data)
        except Exception:
            return response_bad_request("Request denied.")


class TopicAPI(generics.GenericAPIView):
    serializer_class = TopicSerializer

    def get(self, request):
        try:
            topic_list = Topic.objects.all()
            data = TopicSerializer(topic_list, many=True).data
            return response_ok(data)
        except Exception:
            return response_bad_request("Request denied.")
            
    @admin_required
    def post(self, request):
        try:
            data = request.data
            topic_name = data.get('topic_name', '').lower()
            serializer = self.serializer_class(data={'topic_name': topic_name})
            
            if serializer.is_valid() == True:
                if Topic.objects.filter(topic_name=topic_name).exists():
                    return response_bad_request({"topic_name": "This topic already exists!"})
                if topic_name == "":
                    return response_bad_request({"topic_name": "This field cannot be blank."})
                serializer.save()
                return response_ok(serializer.data)

            else:
                return response_bad_request({"entered_data": "Entered data is invalid."})
        except Exception:
            return response_bad_request("Request denied.")

    @admin_required
    def put(self, request):
        data = request.data
        
        if data.get("id","") != "":
            try:
                topic = Topic.objects.get(id=data["id"])
            except Exception:
                return response_bad_request("Topic doesn't exists!")
            if data.get("topic_name", '') != '':
                if Topic.objects.filter(topic_name=data["topic_name"].lower()).exists():
                    return response_bad_request({"topic_name": "This Topic already exists!"})
            topic.topic_name = data['topic_name']
            topic.save()
            return response_ok("Topic was updated!")
        else:
            return response_bad_request({"id": "topic_id is required!"})
            

class DeleteTopicAPI(generics.GenericAPIView):

    @admin_required
    def get(self, request, id):
        try:
            topic = Topic.objects.get(id=id)
            data = TopicSerializer(topic).data
            return response_ok(data)
        except Exception:
            return response_bad_request("Topic does not exist.")

    @admin_required
    def delete(self, request, id):
        try:
            topic = Topic.objects.get(id=id)
            topic.delete()
            return response_no_content("Delete successfully.")

        except Folders.DoesNotExist:
            return response_not_found("Topic does not exist.")
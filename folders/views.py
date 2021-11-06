from rest_framework import generics
from accounts.decorators import login_required
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
            for k, v in data.items():
                if hasattr(folder, k):
                    setattr(folder, k, v)
                else:
                    return response_bad_request(f"Folder object does not have attribute '{k}'")
            folder.save()
            return response_ok(FolderDetailSerializer(folder).data)

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
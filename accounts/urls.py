from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from accounts.views import *

urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('profile/', OwnProfilePageAPI.as_view()),
    #path('profile/<int:id>', ProfilePageAPI.as_view()),
    #path('profile/change-password/', ChangePasswordAPI().as_view()),

    path('login/', LoginAPI.as_view()),
    path('logout/', LogoutAPI.as_view()),

    #path('admin/users/', UserAPI.as_view()),
    #path('admin/users/<int:id>', UserDetailAPI.as_view()),
]

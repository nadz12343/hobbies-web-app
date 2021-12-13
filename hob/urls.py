from django.contrib import admin
from django.urls import path
from hob.views import register, index, logoutUser, loginUser, profile, hobbies, similar_hobbies
from .api import GET_UserAccount, PUT_UserAccount, hobbies_api, addHobby_api, add_hobby_user_list, GET_all_UserAccount, send_friend_request, GET_friend_requests, manage_friend_request, remove_hobby_from_list

urlpatterns = [
    # Account 
    path('admin/', admin.site.urls),
    path('register/', register, name="register"),
    path('logout/', logoutUser, name="logout"),
    path('login/', loginUser, name="login"),

    # API
    path('api/user', GET_UserAccount, name="get-user-details"),
    path('api/update', PUT_UserAccount, name="update-user-details"),
    path('api/hobbies/', hobbies_api, name="api_hobbies"),
    path('api/hobby/post', addHobby_api, name="api_addHobby"),
    path('api/hobby/list', add_hobby_user_list, name="hobby-list"),
    path('api/similarhobbies', GET_all_UserAccount, name="similar-hobbies"),
    path('api/send-request/<int:id>', send_friend_request, name="send-request"),
    path('api/get-requests/', GET_friend_requests, name="get-requests"),
    path('api/manage-request/<int:id>', manage_friend_request, name="manage-request"),
    path('api/remove-hobby/<int:id>', remove_hobby_from_list, name="remove-user-hobby"),

    # Webpages
    path('', index, name="home"),
    path('profile/', profile, name="profile"),
    path('hobbies/', hobbies, name="hobbies"),
    path('similar-hobbies/', similar_hobbies, name="similar")
]
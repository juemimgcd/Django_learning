from django.urls import path

from . import views


urlpatterns = [
    path("api/user/register", views.UserRegisterAPIView.as_view(), name="user-register"),
    path("api/user/login", views.UserLoginAPIView.as_view(), name="user-login"),
    path("api/user/info", views.UserInfoAPIView.as_view(), name="user-info"),
    path("api/user/update", views.UserUpdateAPIView.as_view(), name="user-update"),
    path("api/user/password", views.UserPasswordAPIView.as_view(), name="user-password"),
]


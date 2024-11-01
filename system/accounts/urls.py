from django.urls import path
from . import views

urlpatterns = [
    path("firebase-login/", views.FirebaseLoginView.as_view(), name="firebase_login"),
    path("firebase-register/", views.FirebaseRegisterView.as_view(), name="firebase_register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("face-login/", views.FaceLoginView.as_view(), name="login"),
    path("test/", views.UserProfileView.as_view(), name="test"),
]
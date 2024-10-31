from django.urls import path
from .views import FaceLoginView

urlpatterns = [
    path('api/login/face/', FaceLoginView.as_view(), name='face_login'),
]

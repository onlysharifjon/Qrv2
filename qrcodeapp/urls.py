from django.urls import path
from .views import ImageCreateAPIView,AddPDFAPIView

urlpatterns = [
    path('register/', ImageCreateAPIView.as_view(), name='register api'),
    path('upload/pdf/', AddPDFAPIView.as_view(), name='add pdf'),
]

# cards/urls.py
from django.urls import path
from .views import (
    IDCardCreateAPIView, 
    IDCardDetailAPIView, 
    IDCardDownloadAPIView,
    QRScanAPIView
)

urlpatterns = [
    path('register/', IDCardCreateAPIView.as_view(), name='idcard-create'),
    path('idcards/<uuid:uuid>/', IDCardDetailAPIView.as_view(), name='idcard-detail'),
    path('idcards/<uuid:uuid>/download/', IDCardDownloadAPIView.as_view(), name='idcard-download'),
    path('qr/', QRScanAPIView.as_view(), name='qr-scan'),
]
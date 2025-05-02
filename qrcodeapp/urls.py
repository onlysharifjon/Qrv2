from django.urls import path
from .views import ImageCreateAPIView,AddPDFAPIView,IDCardViewSet,QRScanView

urlpatterns = [
    path('register/', ImageCreateAPIView.as_view(), name='register api'),
    path('upload/pdf/', AddPDFAPIView.as_view(), name='add pdf'),
    path('idcardview',IDCardViewSet.as_view(), name='idcard view'),
    path('qrscan',QRScanView.as_view(), name='QRScan'),
]

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IDCardViewSet, QRScanView

router = DefaultRouter()
router.register(r'idcards', IDCardViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/qr/', QRScanView.as_view(), name='qr-scan'),
]

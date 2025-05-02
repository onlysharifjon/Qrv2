from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger dokumentatsiya uchun schema view
schema_view = get_schema_view(
   openapi.Info(
      title="QR Code API",
      default_version='v1',
      description="QR kodlarni yaratish va boshqarish uchun API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   url=f'https://qr.abdugafforov.uz',  # Bu qatorni qo'shing
   schemes=['https'], 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('qrcodeapp.urls')),
    
    # Swagger dokumentatsiya yo'llari
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Media va statik fayllar uchun yo'llar
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
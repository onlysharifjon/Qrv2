# cards/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import os
import uuid
from .models import IDCard
from .serializers import IDCardSerializer
from .utils import create_id_card, create_qr_code
from django.core.files.base import File
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

class IDCardCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_description="ID karta yaratish va PDF generatsiya qilish",
        manual_parameters=[
            openapi.Parameter(
                'first_name', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Ism'
            ),
            openapi.Parameter(
                'last_name', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Familiya'
            ),
            openapi.Parameter(
                'surname', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Otasining ismi'
            ),
            openapi.Parameter(
                'birthday', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Tug\'ilgan sana'
            ),
            openapi.Parameter(
                'id_pass', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Pasport raqami'
            ),
            openapi.Parameter(
                'country', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Mamlakat'
            ),
            openapi.Parameter(
                'phone', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='Telefon'
            ),
            openapi.Parameter(
                'id_badge', 
                openapi.IN_FORM,
                type=openapi.TYPE_STRING, 
                required=True,
                description='ID raqami'
            ),
            openapi.Parameter(
                'user_image', 
                openapi.IN_FORM,
                type=openapi.TYPE_FILE, 
                required=False,
                description='Foydalanuvchi rasmi'
            ),
        ],
        responses={
            201: openapi.Response(
                description="PDF karta yaratildi",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: "Noto'g'ri ma'lumot kiritildi",
            500: "Serverda xatolik yuz berdi"
        }
    )
    def post(self, request, format=None):
        serializer = IDCardSerializer(data=request.data)
        
        if serializer.is_valid():
            # Saqlash
            instance = serializer.save()
            
            try:
                # PDF yaratish uchun ma'lumotlar tayyorlash
                user_data = {
                    'first_name': instance.first_name,
                    'last_name': instance.last_name,
                    'surname': instance.surname,
                    'birthday': instance.birthday,
                    'id_pass': instance.id_pass,
                    'country': instance.country,
                    'phone': instance.phone,
                    'id_badge': instance.id_badge,
                }
                
                # Rasmlar yo'llari
                user_image_path = None
                if instance.user_image:
                    user_image_path = instance.user_image.path
                
                # QR code yaratish (bizning holda QR kod PDF ni uuid si bo'ladi)
                qr_data = f"{request.build_absolute_uri('/api/qr/')}?uuid={instance.uuid}"
                qr_output_path = os.path.join(settings.MEDIA_ROOT, 'qr_images', f"{instance.uuid}.png")
                os.makedirs(os.path.dirname(qr_output_path), exist_ok=True)
                
                # QR kod yaratish
                qr_image_path = create_qr_code(qr_data, qr_output_path)
                
                # QR kod rasmini modelga saqlash
                with open(qr_image_path, 'rb') as f:
                    instance.qr_image.save(f"{instance.uuid}.png", File(f))
                
                # Shablon PDF yo'li
                template_pdf_path = os.path.join(settings.BASE_DIR, 'templates', 'card.pdf')
                
                # Hosil bo'ladigan PDF fayl yo'li
                output_filename = f"{instance.uuid}.pdf"
                output_pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf_files', output_filename)
                
                # Standart rasm yo'li
                default_image_path = os.path.join(settings.BASE_DIR, 'static', 'default_avatar.png')
                
                # PDF yaratish
                create_id_card(
                    template_pdf_path=template_pdf_path,
                    output_pdf_path=output_pdf_path,
                    user_data=user_data,
                    default_image_path=default_image_path,
                    qr_image_path=qr_image_path,
                    user_image_path=user_image_path
                )
                
                # Yaratilgan PDF faylni modelga saqlash
                with open(output_pdf_path, 'rb') as f:
                    instance.pdf_file.save(output_filename, File(f))
                
                # PDF faylni to'g'ridan-to'g'ri qaytarish
                return FileResponse(
                    open(instance.pdf_file.path, 'rb'),
                    content_type='application/pdf',
                    as_attachment=True,
                    filename=output_filename
                )
                
            except Exception as e:
                # Xatolik yuz bersa, ID karta ma'lumotlarini qaytaramiz
                return Response({
                    'error': f"PDF yaratishda xatolik: {str(e)}",
                    'id_card': serializer.data
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IDCardDetailAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ID karta ma'lumotlarini olish",
        responses={
            200: IDCardSerializer,
            404: "ID karta topilmadi",
            500: "Serverda xatolik yuz berdi"
        }
    )
    def get(self, request, uuid, format=None):
        try:
            id_card = get_object_or_404(IDCard, uuid=uuid)
            serializer = IDCardSerializer(id_card)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': f"Ma'lumotlarni olishda xatolik: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IDCardDownloadAPIView(APIView):
    """
    ID karta PDF faylini yuklab olish uchun API View
    """
    @swagger_auto_schema(
        operation_description="ID karta PDF faylini yuklab olish",
        responses={
            200: openapi.Response(
                description="PDF fayl yuklab olindi",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            404: "PDF fayl topilmadi",
            500: "Serverda xatolik yuz berdi"
        }
    )
    def get(self, request, uuid, format=None):
        try:
            id_card = get_object_or_404(IDCard, uuid=uuid)
            
            if id_card.pdf_file:
                return FileResponse(
                    open(id_card.pdf_file.path, 'rb'),
                    content_type='application/pdf',
                    as_attachment=True,
                    filename=os.path.basename(id_card.pdf_file.name)
                )
            else:
                return Response({
                    'error': "PDF fayl topilmadi"
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': f"PDF faylni olishda xatolik: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRScanAPIView(APIView):
    @swagger_auto_schema(
        operation_description="QR kod skanerlash natijasida PDF faylni ochish",
        manual_parameters=[
            openapi.Parameter(
                'uuid', 
                openapi.IN_QUERY, 
                description="ID kartaning UUID si", 
                type=openapi.TYPE_STRING, 
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="PDF fayl ochildi",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: "UUID parametri ko'rsatilmadi",
            404: "PDF fayl topilmadi",
            500: "Serverda xatolik yuz berdi"
        }
    )
    def get(self, request, format=None):
        uuid = request.query_params.get('uuid')
        
        if not uuid:
            return Response({
                'error': "UUID parametri kerak"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            id_card = get_object_or_404(IDCard, uuid=uuid)
            
            if id_card.pdf_file:
                # PDF ni to'g'ridan-to'g'ri ochish uchun as_attachment=False
                return FileResponse(
                    open(id_card.pdf_file.path, 'rb'),
                    content_type='application/pdf',
                    as_attachment=False,  # PDF ni yuklab olish emas, ko'rsatish
                )
            else:
                return Response({
                    'error': "PDF fayl topilmadi"
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': f"Xatolik yuz berdi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
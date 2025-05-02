import uuid
import os
import qrcode

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Image
from .serializers import ImageSerializer, PdfSerializer


class ImageCreateAPIView(APIView):
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        # Formani tekshirish
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            u_id = uuid.uuid4()

            # QR code yaratish
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(u_id))
            qr.make(fit=True)

            # Fayl nomi va yo‘li
            filename = f"{u_id}.png"
            qr_image_rel_path = os.path.join("uploads", filename)
            qr_image_abs_path = os.path.join(settings.MEDIA_ROOT, qr_image_rel_path)

            # Papkani yaratish agar kerak bo‘lsa
            os.makedirs(os.path.dirname(qr_image_abs_path), exist_ok=True)

            # QR image saqlash
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image.save(qr_image_abs_path)

            # (Ixtiyoriy) PDF faylni hozircha bo‘sh saqlaymiz
            dummy_pdf_path = os.path.join("uploads", f"{u_id}.pdf")
            dummy_pdf_abs = os.path.join(settings.MEDIA_ROOT, dummy_pdf_path)
            with open(dummy_pdf_abs, "wb") as pdf_file:
                pdf_file.write(b"%PDF-1.4\n% Dummy PDF\n%%EOF")

            # Modelni saqlash
            serializer.save(
                u_id = u_id,
                qr_image = qr_image_rel_path,
                pdf_file = None  # pdf_file hozircha yo‘q
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Image


class AddPDFAPIView(APIView):
    serializer_class = PdfSerializer
    def post(self, request, *args, **kwargs):
        u_id = request.data.get("u_id")
        pdf_file = request.FILES.get("pdf_file")  # FILE sifatida olish MUHIM!

        if not u_id or not pdf_file:
            return Response({'error': 'u_id va pdf_file kerak'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image_instance = Image.objects.get(u_id=u_id)
        except Image.DoesNotExist:
            return Response({'error': 'Image topilmadi'}, status=status.HTTP_404_NOT_FOUND)

        image_instance.pdf_file = pdf_file
        image_instance.save()

        return Response({'message': 'PDF yuklandi'}, status=status.HTTP_200_OK)


# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import os
from .models import IDCard
from .serializers import IDCardSerializer
from .utils import create_id_card, create_qr_code
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView


class IDCardViewSet(viewsets.ModelViewSet):
    queryset = IDCard.objects.all()
    serializer_class = IDCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Saqlash
        instance = serializer.save()

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
        from django.core.files.base import File
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
            user_image_path=user_image_path,
            qr_image_path=qr_image_path,
            default_image_path=default_image_path
        )

        # Yaratilgan PDF faylni modelga saqlash
        with open(output_pdf_path, 'rb') as f:
            instance.pdf_file.save(output_filename, File(f))

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        id_card = self.get_object()
        if id_card.pdf_file:
            return FileResponse(
                open(id_card.pdf_file.path, 'rb'),
                as_attachment=True,
                filename=os.path.basename(id_card.pdf_file.name)
            )
        return Response(
            {"error": "PDF fayl mavjud emas"},
            status=status.HTTP_404_NOT_FOUND
        )


# QR kod skanlash uchun API (QR kod UUID ni o'qiganda ishlaydi)
class QRScanView(APIView):
    def get(self, request):
        uuid = request.query_params.get('uuid')

        if not uuid:
            return Response(
                {"error": "UUID parametri kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            id_card = get_object_or_404(IDCard, uuid=uuid)

            if id_card.pdf_file:
                return FileResponse(
                    open(id_card.pdf_file.path, 'rb'),
                    content_type='application/pdf',
                    filename=os.path.basename(id_card.pdf_file.name)
                )
            else:
                return Response(
                    {"error": "PDF fayl topilmadi"},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return Response(
                {"error": f"Xatolik yuz berdi: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

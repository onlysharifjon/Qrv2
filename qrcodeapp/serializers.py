from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "u_id",          # UUID ham qaytariladi
            "first_name",
            "last_name",
            "middle_name",
            "country",
            "birth_date",
            "passport",
            "phone",
            "id_badge",
            "qr_image",      # QR rasm URL
            "pdf_file",      # PDF fayl URL
            "created_at",    # Tizimda yaratilgan vaqt
        ]
        read_only_fields = ["u_id", "qr_image", "pdf_file", "created_at"]
class PdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "pdf_file",
            'u_id'
        ]

# serializers.py
from rest_framework import serializers
from .models import IDCard

class IDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCard
        fields = ['id', 'uuid', 'first_name', 'last_name', 'surname', 'birthday',
                  'id_pass', 'country', 'phone', 'id_badge', 'user_image',
                  'qr_image', 'pdf_file', 'created_at']
        read_only_fields = ['uuid', 'pdf_file', 'created_at']

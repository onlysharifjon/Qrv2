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

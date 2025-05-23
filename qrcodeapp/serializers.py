from rest_framework import serializers
from .models import IDCard

class IDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCard
        fields = ['id', 'uuid', 'first_name', 'gender', 'birthday',
                  'id_pass', 'country', 'blood_type', 'id_badge', 'user_image',
                  'qr_image', 'pdf_file', 'created_at']
        read_only_fields = ['uuid', 'qr_image', 'pdf_file', 'created_at']
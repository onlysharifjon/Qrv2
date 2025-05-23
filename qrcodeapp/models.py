from django.db import models
import uuid
import os

def generate_pdf_path(instance, filename):
    """PDF fayllar uchun yo'l yaratish"""
    return os.path.join('pdf_files', f"{instance.uuid}.pdf")

def generate_user_image_path(instance, filename):
    """Foydalanuvchi rasmlari uchun yo'l yaratish"""
    ext = filename.split('.')[-1]
    return os.path.join('user_images', f"{instance.uuid}.{ext}")

def generate_qr_image_path(instance, filename):
    """QR kod rasmlari uchun yo'l yaratish"""
    ext = filename.split('.')[-1]
    return os.path.join('qr_images', f"{instance.uuid}.{ext}")

class IDCard(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    surname = models.CharField(max_length=100,null=True)
    birthday = models.CharField(max_length=20)
    id_pass = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    blood_type = models.CharField(max_length=20)
    id_badge = models.CharField(max_length=20)
    user_image = models.ImageField(upload_to=generate_user_image_path, null=True, blank=True)
    qr_image = models.ImageField(upload_to=generate_qr_image_path, null=True, blank=True)
    pdf_file = models.FileField(upload_to=generate_pdf_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} ({self.uuid})"
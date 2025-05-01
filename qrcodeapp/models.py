from django.db import models

# Create your models here.
import uuid
from django.db import models


class Image(models.Model):
    u_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    birth_date = models.CharField(max_length=255)
    passport = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    id_badge = models.CharField(max_length=255)
    qr_image = models.FileField(upload_to='uploads/')
    pdf_file = models.FileField(upload_to='uploads/',null = True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Generated by Django 5.2 on 2025-05-01 18:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('u_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(max_length=255)),
                ('birth_date', models.CharField(max_length=255)),
                ('passport', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('id_badge', models.CharField(max_length=255)),
                ('qr_image', models.FileField(upload_to='uploads/')),
                ('pdf_file', models.FileField(null=True, upload_to='uploads/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

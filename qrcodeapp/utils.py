# utils.py
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red, blue, green, black, white, HexColor
import qrcode
from PIL import Image
import os
from django.conf import settings


def create_qr_code(data, output_path):
    """
    UUID asosida QR kod yaratish
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(output_path)
    return output_path


def create_id_card(template_pdf_path, output_pdf_path, user_data, user_image_path=None, qr_image_path=None,
                   default_image_path=None):
    """
    ID karta shabloniga ma'lumotlarni joylashtirish
    """
    # PDF hujjatini o'qish
    reader = PdfReader(template_pdf_path)
    writer = PdfWriter()

    # Birinchi sahifani olish
    page = reader.pages[0]

    # PDF sahifa o'lchamlarini olish
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)

    # Rasmni joylashtirish va matnlarni yozish uchun packet yaratish
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Ranglar sozlamalari
    name_color = HexColor("#0000A0")  # To'q ko'k rang - ismi, familiya va surname uchun
    id_badge_color = red  # Qizil - ID raqami uchun
    id_pass_color = blue  # Ko'k - pasport raqami uchun
    info_color = HexColor("#006400")  # To'q yashil - boshqa maydonlar uchun

    # Maydonlar koordinatalari
    id_badge_x = 60  # ID badge
    id_badge_y = 30

    surname_x = 145  # Surname
    surname_y = 276

    last_name_x = 180  # Last name
    last_name_y = 298

    first_name_x = 180  # First name
    first_name_y = 320

    qr_code_x = 180  # QR kod
    qr_code_y = 10
    qr_code_w = 60
    qr_code_h = 60

    birthday_x = 75  # Tug'ilgan sana
    birthday_y = 194

    id_pass_x = 270  # Pasport
    id_pass_y = 194

    country_x = 260  # Mamlakat
    country_y = 125

    phone_x = 230  # Telefon
    phone_y = 92

    user_image_x = 140  # Foydalanuvchi rasmi
    user_image_y = 350
    user_image_w = 140
    user_image_h = 140

    # Foydalanuvchi rasmini joylashtirish
    if user_image_path and os.path.exists(user_image_path):
        image_path = user_image_path
    else:
        if default_image_path and os.path.exists(default_image_path):
            image_path = default_image_path
        else:
            # Bo'sh rasm yaratamiz
            blank_image = Image.new('RGB', (user_image_w, user_image_h), color='white')
            temp_blank_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'blank_image.png')
            os.makedirs(os.path.dirname(temp_blank_path), exist_ok=True)
            blank_image.save(temp_blank_path)
            image_path = temp_blank_path

    # Rasmni joylashtiramiz
    img = Image.open(image_path)
    img = img.resize((user_image_w, user_image_h), Image.LANCZOS)

    # RGBA ni RGB ga aylantirish
    if img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img

    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_user_img.png')
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    img.save(temp_path)
    can.drawImage(temp_path, user_image_x, user_image_y, width=user_image_w, height=user_image_h)

    # QR kod joylashtirish
    if qr_image_path and os.path.exists(qr_image_path):
        qr_img = Image.open(qr_image_path)
        qr_img = qr_img.resize((qr_code_w, qr_code_h), Image.LANCZOS)

        if qr_img.mode == 'RGBA':
            rgb_qr = Image.new('RGB', qr_img.size, (255, 255, 255))
            rgb_qr.paste(qr_img, mask=qr_img.split()[3])
            qr_img = rgb_qr

            temp_qr_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_qr_img.png')
            qr_img.save(temp_qr_path)
            can.drawImage(temp_qr_path, qr_code_x, qr_code_y, width=qr_code_w, height=qr_code_h)

        # Matnlarni joylashtirish
        # Isim ma'lumotlari
        can.setFont("Helvetica-Bold", 16)

        if "first_name" in user_data:
            can.setFillColor(name_color)
            can.drawString(first_name_x, first_name_y, str(user_data["first_name"]))

        if "last_name" in user_data:
            can.setFillColor(name_color)
            can.drawString(last_name_x, last_name_y, str(user_data["last_name"]))

        if "surname" in user_data:
            can.setFillColor(name_color)
            can.drawString(surname_x, surname_y, str(user_data["surname"]))

        # ID badge
        if "id_badge" in user_data:
            can.setFillColor(id_badge_color)
            can.drawString(id_badge_x, id_badge_y, str(user_data["id_badge"]))

        # Boshqa ma'lumotlar
        can.setFont("Helvetica", 14)

        if "birthday" in user_data:
            can.setFillColor(info_color)
            can.drawString(birthday_x, birthday_y, str(user_data["birthday"]))

        if "id_pass" in user_data:
            can.setFillColor(id_pass_color)
            can.drawString(id_pass_x, id_pass_y, str(user_data["id_pass"]))

        if "country" in user_data:
            can.setFillColor(info_color)
            can.drawString(country_x, country_y, str(user_data["country"]))

        if "phone" in user_data:
            can.setFillColor(info_color)
            can.drawString(phone_x, phone_y, str(user_data["phone"]))

        can.save()

        # PDF yaratish
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])

        writer.add_page(page)

        # Yangi PDF-ni saqlash
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        # Vaqtinchalik fayllarni tozalash
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if 'temp_qr_path' in locals() and os.path.exists(temp_qr_path):
                os.remove(temp_qr_path)
            if image_path.endswith('blank_image.png') and os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Fayl tozalashda xatolik: {e}")

        return output_pdf_path

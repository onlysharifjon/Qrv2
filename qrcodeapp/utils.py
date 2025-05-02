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

    Args:
        template_pdf_path (str): Shablon PDF fayl yo'li
        output_pdf_path (str): Yangi PDF fayl yo'li
        user_data (dict): Foydalanuvchi ma'lumotlari
        user_image_path (str): Foydalanuvchi rasmi fayl yo'li
        qr_image_path (str): QR kod rasmi fayl yo'li
        default_image_path (str): Standart rasm fayl yo'li
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

    # Qizil quti markaziga ID raqamini joylashtirish
    id_badge_x = 60  # O'ng tomonda
    id_badge_y = 30  # Tepada, nusik Card yozuvi yonida

    # Maydonlar koordinatalari - PDF fayl o'lchamiga qarab
    # Chap tomondagi ma'lumotlar
    min_x = 120
    max_x = 300
    center_x = (min_x + max_x) / 2  # Oraliq markazi (210)

    # Familiya, Ism va Otasining ismi uchun koordinatalar
    surname_x = center_x  # Markazlashtirilgan (210)
    surname_y = 276  # Yuqoridagi matn

    last_name_x = center_x
    last_name_y = 298  # O'rtadagi matn

    first_name_x = center_x
    first_name_y = 320  # Last name dan pastroq

    # QR kod, hozircha bo'sh
    qr_code_x = 180
    qr_code_y = 10
    qr_code_w = 60
    qr_code_h = 60

    # Pasport va boshqa maydonlar
    birthday_x = 75  # DoB qutisidagi
    birthday_y = 194  # Pastki qismida

    id_pass_x = 270  # Pasport qutisida
    id_pass_y = 194  # Pastki qismida

    # Service Provider Information qutisi ichida
    country_x = 260
    country_y = 125

    phone_x = 230
    phone_y = 92

    # Rasmi joylashtirish qismi
    user_image_x = 140  # Pastki chap qism
    user_image_y = 350  # Ancha pastda
    user_image_w = 140
    user_image_h = 140

    # Foydalanuvchi rasmini joylashtirish
    if user_image_path and os.path.exists(user_image_path):
        # Foydalanuvchi rasmi mavjud bo'lsa, uni joylashtiramiz
        image_path = user_image_path
    else:
        # Foydalanuvchi rasmi yo'q bo'lsa, standart rasmni joylashtiramiz
        if default_image_path and os.path.exists(default_image_path):
            image_path = default_image_path
        else:
            # Standart rasm ham yo'q bo'lsa, bo'sh rasm yaratamiz
            blank_image = Image.new('RGB', (user_image_w, user_image_h), color='white')
            temp_blank_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'blank_image.png')
            os.makedirs(os.path.dirname(temp_blank_path), exist_ok=True)
            blank_image.save(temp_blank_path)
            image_path = temp_blank_path

    # Rasmni joylashtiramiz (foydalanuvchi rasmi yoki standart rasm)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((user_image_w, user_image_h), Image.LANCZOS)

        # RGBA formatini tekshirib, zarur bo'lsa RGB ga o'tkazamiz
        if img.mode == 'RGBA':
            # RGBA formatini RGB ga o'tkazamiz
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # 3-kanal - bu alfa kanal
            img = rgb_img

        # Rasmni PNG formatida saqlaymiz - JPEG muammolaridan qochish uchun
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_user_img.png')
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        img.save(temp_path)
        can.drawImage(temp_path, user_image_x, user_image_y, width=user_image_w, height=user_image_h)

        try:
            os.remove(temp_path)
        except:
            pass

    # QR kod yaratish va joylashtirish
    if qr_image_path and os.path.exists(qr_image_path):
        # Tayyor QR kod rasmini joylashtiramiz
        qr_img = Image.open(qr_image_path)
        qr_img = qr_img.resize((qr_code_w, qr_code_h), Image.LANCZOS)

        # RGBA formatini tekshirib, zarur bo'lsa RGB ga o'tkazamiz
        if qr_img.mode == 'RGBA':
            # RGBA formatini RGB ga o'tkazamiz
            rgb_qr = Image.new('RGB', qr_img.size, (255, 255, 255))
            rgb_qr.paste(qr_img, mask=qr_img.split()[3])  # 3-kanal - bu alfa kanal
            qr_img = rgb_qr

        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_qr_img.png')
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        qr_img.save(temp_path)
        can.drawImage(temp_path, qr_code_x, qr_code_y, width=qr_code_w, height=qr_code_h)

        try:
            os.remove(temp_path)
        except:
            pass

    # Shriftni sozlash - o'zbek/arab harflari uchun
    can.setFont("Helvetica-Bold", 16)

    # Matnlarni joylashtirish
    # Isim ma'lumotlari - chap tomondan
    if "first_name" in user_data:
        text = str(user_data["first_name"])
        text_width = can.stringWidth(text, "Helvetica-Bold", 16)
        text_x = first_name_x - text_width / 2

        # Chegaralar tekshiruvi
        if text_x < min_x:
            text_x = min_x
        elif text_x + text_width > max_x:
            text_x = max_x - text_width

        can.setFillColor(name_color)
        can.drawString(text_x, first_name_y, text)

    if "last_name" in user_data:
        text = str(user_data["last_name"])
        text_width = can.stringWidth(text, "Helvetica-Bold", 16)
        text_x = last_name_x - text_width / 2

        # Chegaralar tekshiruvi
        if text_x < min_x:
            text_x = min_x
        elif text_x + text_width > max_x:
            text_x = max_x - text_width

        can.setFillColor(name_color)
        can.drawString(text_x, last_name_y, text)

    if "surname" in user_data:
        text = str(user_data["surname"])
        text_width = can.stringWidth(text, "Helvetica-Bold", 16)
        text_x = surname_x - text_width / 2

        # Chegaralar tekshiruvi - chap tomonga chiqib ketmasligi uchun
        if text_x < min_x:
            text_x = min_x
        # O'ng tomonga chiqib ketmasligi uchun
        elif text_x + text_width > max_x:
            text_x = max_x - text_width

        can.setFillColor(name_color)
        can.drawString(text_x, surname_y, text)

    # ID badge - qizil quti yonida
    if "id_badge" in user_data:
        can.setFillColor(id_badge_color)
        can.drawString(id_badge_x, id_badge_y, str(user_data["id_badge"]))

    # Pasport va boshqa ma'lumotlar
    can.setFont("Helvetica", 14)  # Kichikroq shrift

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

    # Yangi ma'lumotlarni PDF ga qo'shish
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page.merge_page(new_pdf.pages[0])

    # Yangi PDF-ni saqlash
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    # Vaqtinchalik fayllarni tozalash
    try:
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_user_img.png')):
            os.remove(os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_user_img.png'))
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_qr_img.png')):
            os.remove(os.path.join(settings.MEDIA_ROOT, 'temp', 'temp_qr_img.png'))
        if image_path.endswith('blank_image.png') and os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        print(f"Fayl tozalashda xatolik: {e}")

    return output_pdf_path

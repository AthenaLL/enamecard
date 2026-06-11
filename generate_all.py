import json
from openpyxl import load_workbook
import qrcode
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# =========================
# SETTINGS
# =========================
EXCEL_FILE = "staff.xlsx"
SHEET_NAME = "staff"

BASE_URL = "https://enamecard-one.vercel.app"

PEOPLE_JSON = "people.json"

CONTACT_DIR = Path("contacts")
QR_DIR = Path("qr")
DESIGNED_QR_DIR = Path("designed_qr")

CONTACT_DIR.mkdir(exist_ok=True)
QR_DIR.mkdir(exist_ok=True)
DESIGNED_QR_DIR.mkdir(exist_ok=True)

# =========================
# READ EXCEL
# =========================
wb = load_workbook(EXCEL_FILE, data_only=True)
ws = wb[SHEET_NAME]

headers = [cell.value for cell in ws[1]]
people = {}

for row_values in ws.iter_rows(min_row=2, values_only=True):
    row = dict(zip(headers, row_values))

    person_id = str(row.get("id") or "").strip()

    if person_id == "":
        continue

    name = str(row["name"]).strip()
    title = str(row["title"]).strip()
    company = str(row["company"]).strip()
    phone = str(row["phone"]).strip()
    email = str(row["email"]).strip()
    whatsapp = str(row["whatsapp"]).strip()
    website = str(row["website"]).strip()
    photo = str(row["photo"]).strip()

    vcf_path = f"contacts/{person_id}.vcf"

    people[person_id] = {
        "name": name,
        "title": title,
        "company": company,
        "phone": phone,
        "email": email,
        "whatsapp": whatsapp,
        "website": website,
        "photo": photo,
        "vcf": vcf_path
    }

    # =========================
    # GENERATE VCF
    # =========================
    vcf_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{company}
TITLE:{title}
TEL;TYPE=WORK,CELL:+{phone}
EMAIL:{email}
URL:{website}
END:VCARD
"""

    with open(CONTACT_DIR / f"{person_id}.vcf", "w", encoding="utf-8") as f:
        f.write(vcf_content)

    # =========================
    # GENERATE QR
    # =========================
    url = f"{BASE_URL}/?id={person_id}"

    qr = qrcode.QRCode(
        version=1,
        box_size=12,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    qr_img.save(QR_DIR / f"{person_id}.png")

    # =========================
    # GENERATE DESIGNED QR CARD
    # =========================
    card_width = 1300
    card_height = 800

    card = Image.new("RGB", (card_width, card_height), "#000000")
    draw = ImageDraw.Draw(card)

    # =========================
    # BORDER
    # =========================
    draw.rounded_rectangle(
        [35, 35, card_width - 35, card_height - 35],
        radius=45,
        outline="#FFD700",
        width=7
    )

    # =========================
    # LOGO
    # =========================
    logo_path = r"C:\Users\itdep\OneDrive\Documents\Qian\ENameCard\1668754061_logotoppanelv2sengli.png"

    try:
        logo = Image.open(logo_path).convert("RGBA")

        logo_max_width = 430
        logo_max_height = 150

        logo.thumbnail(
            (logo_max_width, logo_max_height),
            Image.LANCZOS
        )

        card.paste(
            logo,
            (105, 80),
            logo
        )

    except Exception as e:
        print(f"Logo error: {e}")

    # =========================
    # FONTS
    # =========================
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 76)
        font_title = ImageFont.truetype("arialbd.ttf", 46)
        font_company = ImageFont.truetype("arial.ttf", 34)
    except:
        font_name = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_company = ImageFont.load_default()

    # =========================
    # CONTENT POSITION
    # =========================
    content_center_y = 480

    # =========================
    # QR
    # =========================
    qr_size = 250
    qr_padding = 30

    qr_resized = qr_img.resize(
        (qr_size, qr_size),
        Image.LANCZOS
    )

    qr_x = 880
    qr_y = int(content_center_y - qr_size / 2)

    draw.rounded_rectangle(
        [
            qr_x - qr_padding,
            qr_y - qr_padding,
            qr_x + qr_size + qr_padding,
            qr_y + qr_size + qr_padding
        ],
        radius=28,
        fill="white"
    )

    card.paste(
        qr_resized,
        (qr_x, qr_y)
    )

    # =========================
    # LEFT TEXT
    # =========================
    left_x = 115

    line_name = 95
    line_title = 75
    line_company = 65

    total_text_height = line_name + line_title + line_company

    text_margin_top = 20

    text_start_y = (
        content_center_y
        - total_text_height / 2
        + text_margin_top
    )

    draw.text(
        (left_x, text_start_y),
        name,
        fill="#FFD700",
        font=font_name,
        anchor="lm"
    )

    draw.text(
        (left_x, text_start_y + line_name),
        title,
        fill="white",
        font=font_title,
        anchor="lm"
    )

    draw.text(
        (left_x, text_start_y + line_name + line_title),
        company,
        fill="white",
        font=font_company,
        anchor="lm"
    )

    # =========================
    # VERTICAL LINE
    # =========================
    line_x = 730
    line_top = int(content_center_y - 145)
    line_bottom = int(content_center_y + 145)

    draw.line(
        [(line_x, line_top), (line_x, line_bottom)],
        fill="#FFD700",
        width=5
    )

    # =========================
    # SAVE DESIGNED CARD
    # =========================
    card.save(
        DESIGNED_QR_DIR / f"{person_id}_enamecard.png"
    )

# =========================
# EXPORT people.json
# =========================
with open(PEOPLE_JSON, "w", encoding="utf-8") as f:
    json.dump(people, f, ensure_ascii=False, indent=2)

print("Done.")
print("Generated:")
print("- people.json")
print("- contacts/*.vcf")
print("- qr/*.png")
print("- designed_qr/*.png")
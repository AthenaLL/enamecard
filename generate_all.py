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

BASE_URL = "https://athenall.github.io/enamecard"

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

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img.save(QR_DIR / f"{person_id}.png")

    # =========================
    # GENERATE DESIGNED QR CARD
    # =========================
    card_width = 900
    card_height = 1300

    card = Image.new("RGB", (card_width, card_height), "#000000")
    draw = ImageDraw.Draw(card)

    # Yellow border
    draw.rounded_rectangle(
        [40, 40, card_width - 40, card_height - 40],
        radius=40,
        outline="#FFD700",
        width=6
    )

    # Title text
    try:
        font_name = ImageFont.truetype("arial.ttf", 60)
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except:
        font_name = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((card_width / 2, 150), name, fill="#FFD700", font=font_name, anchor="mm")
    draw.text((card_width / 2, 230), title, fill="white", font=font_title, anchor="mm")
    draw.text((card_width / 2, 290), company, fill="white", font=font_small, anchor="mm")

    # QR position
    qr_size = 520
    qr_resized = qr_img.resize((qr_size, qr_size))

    qr_x = (card_width - qr_size) // 2
    qr_y = 420

    # White QR background
    draw.rounded_rectangle(
        [qr_x - 30, qr_y - 30, qr_x + qr_size + 30, qr_y + qr_size + 30],
        radius=30,
        fill="white"
    )

    card.paste(qr_resized, (qr_x, qr_y))

    # # Footer
    # draw.text(
    #     (card_width / 2, 1040),
    #     "Scan to save my contact",
    #     fill="#FFD700",
    #     font=font_title,
    #     anchor="mm"
    # )

    # draw.text(
    #     (card_width / 2, 1110),
    #     url,
    #     fill="white",
    #     font=font_small,
    #     anchor="mm"
    # )

    card.save(DESIGNED_QR_DIR / f"{person_id}_enamecard.png")

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
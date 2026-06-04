import qrcode
from pathlib import Path

base_url = "https://senglienamecard.netlify.app"

people = ["qianhui", "jared"]

# 建立 qr folder
Path("qr").mkdir(exist_ok=True)

for person in people:
    url = f"{base_url}/?id={person}"

    img = qrcode.make(url)

    img.save(f"qr/{person}_qr.png")

    print(f"Generated: qr/{person}_qr.png")
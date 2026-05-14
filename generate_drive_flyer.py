"""Generate a print-ready A4 flyer (PDF) encouraging Drive customers
to leave a 5-star Expedia review. Embeds a QR code pointing to the
Drive landing page that walks customers through finding their survey email.
"""

from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

OUT_PATH = "drive-expedia-review-flyer.pdf"
LANDING_URL = "https://alvarocabezali-cell.github.io/NU-SURVEY-PAGE/drive.html"
LOGO_PATH = "drive-logo.png"
PAGE_SIZE = (150 * mm, 150 * mm)

DRIVE_PURPLE = HexColor("#3d1f7a")
DRIVE_PURPLE_DARK = HexColor("#2a1556")
INK = HexColor("#1a1a2e")
MUTED = HexColor("#5a5a6e")
GOLD = HexColor("#f5b400")
SOFT_BG = HexColor("#f5f1ff")


def build_qr(url: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_star(c, cx, cy, size, fill):
    import math
    c.setFillColor(fill)
    c.setStrokeColor(fill)
    p = c.beginPath()
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.45
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def main():
    page_w, page_h = PAGE_SIZE
    c = canvas.Canvas(OUT_PATH, pagesize=PAGE_SIZE)
    c.setTitle("Drive Rental Cars — Leave us a review on Expedia")

    # Top purple accent stripe (full width)
    accent_h = 4 * mm
    c.setFillColor(DRIVE_PURPLE)
    c.rect(0, page_h - accent_h, page_w, accent_h, stroke=0, fill=1)

    # Logo
    logo = ImageReader(LOGO_PATH)
    lw, lh = logo.getSize()
    target_h = 15 * mm
    target_w = target_h * (lw / lh)
    logo_y = page_h - accent_h - 6 * mm - target_h
    c.drawImage(
        logo,
        (page_w - target_w) / 2,
        logo_y,
        width=target_w,
        height=target_h,
        mask="auto",
    )

    # Headline
    y = logo_y - 9 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_w / 2, y, "Loved your ride?")

    y -= 7 * mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DRIVE_PURPLE)
    c.drawCentredString(page_w / 2, y, "Tell Expedia about it")

    # Five gold stars
    y -= 7 * mm
    star_size = 3 * mm
    gap = 2 * mm
    total = 5 * (star_size * 2) + 4 * gap
    start_x = (page_w - total) / 2 + star_size
    for i in range(5):
        draw_star(c, start_x + i * (star_size * 2 + gap), y, star_size, GOLD)

    # QR code
    qr_img = build_qr(LANDING_URL)
    qr_size = 70 * mm
    qr_y = 16 * mm
    c.drawImage(
        qr_img,
        (page_w - qr_size) / 2,
        qr_y,
        width=qr_size,
        height=qr_size,
    )

    # "Scan to leave a review"
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(DRIVE_PURPLE_DARK)
    c.drawCentredString(page_w / 2, 9 * mm, "Scan to leave a review")

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(page_w / 2, 4.5 * mm, "Thank you for choosing Drive Rental Cars")

    c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

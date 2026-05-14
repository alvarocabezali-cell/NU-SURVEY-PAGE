"""Generate a print-ready A4 flyer (PDF) encouraging Drive customers
to leave a 5-star Expedia review. Embeds a QR code pointing to the
Drive landing page that walks customers through finding their survey email.
"""

from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

OUT_PATH = "drive-expedia-review-flyer.pdf"
LANDING_URL = "https://alvarocabezali-cell.github.io/NU-SURVEY-PAGE/drive.html"
LOGO_PATH = "drive-logo.png"

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
    page_w, page_h = A4
    c = canvas.Canvas(OUT_PATH, pagesize=A4)
    c.setTitle("Drive Rental Cars — Leave us a review on Expedia")

    margin = 18 * mm
    inner_w = page_w - 2 * margin

    # Outer rounded card
    c.setFillColor(HexColor("#ffffff"))
    c.setStrokeColor(HexColor("#e2d9f5"))
    c.setLineWidth(1.2)
    c.roundRect(margin, margin, inner_w, page_h - 2 * margin,
                10 * mm, stroke=1, fill=1)

    # Top accent bar (thin purple stripe inside the card)
    accent_h = 6 * mm
    c.setFillColor(DRIVE_PURPLE)
    c.roundRect(margin, page_h - margin - accent_h, inner_w, accent_h,
                3 * mm, stroke=0, fill=1)
    c.rect(margin, page_h - margin - accent_h,
           inner_w, accent_h / 2, stroke=0, fill=1)

    # Logo on white background
    logo_top = page_h - margin - accent_h - 14 * mm
    logo = ImageReader(LOGO_PATH)
    lw, lh = logo.getSize()
    target_h = 26 * mm
    target_w = target_h * (lw / lh)
    c.drawImage(
        logo,
        (page_w - target_w) / 2,
        logo_top - target_h,
        width=target_w,
        height=target_h,
        mask="auto",
    )

    # Headline
    y = logo_top - target_h - 14 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(page_w / 2, y, "Loved your ride?")

    y -= 11 * mm
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(DRIVE_PURPLE)
    c.drawCentredString(page_w / 2, y, "Tell Expedia about it")

    # Five gold stars
    y -= 14 * mm
    star_size = 7 * mm
    gap = 4 * mm
    total = 5 * (star_size * 2) + 4 * gap
    start_x = (page_w - total) / 2 + star_size
    for i in range(5):
        draw_star(c, start_x + i * (star_size * 2 + gap), y, star_size, GOLD)

    # Body copy
    y -= 16 * mm
    c.setFont("Helvetica", 13)
    c.setFillColor(MUTED)
    lines = [
        "Your 5-star review on Expedia helps other travellers",
        "find us — and means the world to our small team.",
        "It only takes 30 seconds.",
    ]
    for line in lines:
        c.drawCentredString(page_w / 2, y, line)
        y -= 6 * mm

    # QR panel
    y -= 6 * mm
    panel_w = 92 * mm
    panel_h = 92 * mm
    panel_x = (page_w - panel_w) / 2
    panel_y = y - panel_h
    c.setFillColor(SOFT_BG)
    c.setStrokeColor(HexColor("#d9ccf5"))
    c.setLineWidth(1)
    c.roundRect(panel_x, panel_y, panel_w, panel_h, 6 * mm, stroke=1, fill=1)

    qr_img = build_qr(LANDING_URL)
    qr_size = 76 * mm
    c.drawImage(
        qr_img,
        (page_w - qr_size) / 2,
        panel_y + (panel_h - qr_size) / 2,
        width=qr_size,
        height=qr_size,
    )

    # "Scan with your phone camera"
    y = panel_y - 8 * mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DRIVE_PURPLE_DARK)
    c.drawCentredString(page_w / 2, y, "Scan with your phone camera")

    y -= 6 * mm
    c.setFont("Helvetica", 10.5)
    c.setFillColor(MUTED)
    c.drawCentredString(
        page_w / 2,
        y,
        "Or visit: alvarocabezali-cell.github.io/NU-SURVEY-PAGE/drive.html",
    )

    # Footer line
    foot_y = margin + 10 * mm
    c.setStrokeColor(HexColor("#e2d9f5"))
    c.setLineWidth(0.6)
    c.line(margin + 12 * mm, foot_y + 6 * mm,
           page_w - margin - 12 * mm, foot_y + 6 * mm)

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(MUTED)
    c.drawCentredString(
        page_w / 2,
        foot_y,
        "Thank you for choosing Drive Rental Cars",
    )

    c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

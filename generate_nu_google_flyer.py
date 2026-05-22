"""Generate a print-ready 15x15 cm flyer (PDF) encouraging NU Car Rentals
customers at LAX to leave a 5-star Google review. Embeds a crisp QR code that
points to the NU Google Business Profile review link.
"""

from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT_PATH = "nu-lax-google-review-flyer.pdf"
# Google Business Profile "leave a review" link for NU Car Rentals @ LAX.
REVIEW_URL = (
    "https://g.page/r/CUDb6EKDYV44EBM/review"
    "?utm_source=gbp&utm_medium=reviews&utm_campaign=qr"
)
LOGO_PATH = "nu-logo.jpg"
PAGE_SIZE = (150 * mm, 150 * mm)

NU_GREEN = HexColor("#5aab1e")
NU_GREEN_DARK = HexColor("#3d7a14")
NU_TEAL = HexColor("#003B49")
MUTED = HexColor("#5a5a6e")
GOLD = HexColor("#f5b400")

# Google brand colours, per-letter, for the "Google" wordmark.
GOOGLE_LETTERS = [
    ("G", HexColor("#4285F4")),
    ("o", HexColor("#EA4335")),
    ("o", HexColor("#FBBC05")),
    ("g", HexColor("#4285F4")),
    ("l", HexColor("#34A853")),
    ("e", HexColor("#EA4335")),
]


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


def draw_google_wordmark(c, cx, cy, font_size):
    """Draw the multicolour 'Google' wordmark centred horizontally on cx."""
    font = "Helvetica-Bold"
    total = sum(stringWidth(ch, font, font_size) for ch, _ in GOOGLE_LETTERS)
    x = cx - total / 2
    c.setFont(font, font_size)
    for ch, colour in GOOGLE_LETTERS:
        c.setFillColor(colour)
        c.drawString(x, cy, ch)
        x += stringWidth(ch, font, font_size)


def main():
    page_w, page_h = PAGE_SIZE
    c = canvas.Canvas(OUT_PATH, pagesize=PAGE_SIZE)
    c.setTitle("NU Car Rentals (LAX) - Leave us a Google review")

    # Top green accent stripe (full width)
    accent_h = 4 * mm
    c.setFillColor(NU_GREEN)
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

    # Location tag
    y = logo_y - 6 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(page_w / 2, y, "LOS ANGELES INTERNATIONAL AIRPORT (LAX)")

    # Headline
    y -= 8 * mm
    c.setFillColor(NU_TEAL)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_w / 2, y, "Loved your ride?")

    y -= 7 * mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(NU_GREEN)
    c.drawCentredString(page_w / 2, y, "Leave us a 5-star Google review")

    # Five gold stars
    y -= 7 * mm
    star_size = 3 * mm
    gap = 2 * mm
    total = 5 * (star_size * 2) + 4 * gap
    start_x = (page_w - total) / 2 + star_size
    for i in range(5):
        draw_star(c, start_x + i * (star_size * 2 + gap), y, star_size, GOLD)

    # QR code
    qr_img = build_qr(REVIEW_URL)
    qr_size = 66 * mm
    qr_y = 18 * mm
    c.drawImage(
        qr_img,
        (page_w - qr_size) / 2,
        qr_y,
        width=qr_size,
        height=qr_size,
    )

    # "Scan to review us on Google" (with multicolour Google wordmark)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(NU_GREEN_DARK)
    prefix = "Scan to review us on "
    prefix_w = stringWidth(prefix, "Helvetica-Bold", 12)
    google_w = sum(stringWidth(ch, "Helvetica-Bold", 12) for ch, _ in GOOGLE_LETTERS)
    line_start = (page_w - (prefix_w + google_w)) / 2
    c.drawString(line_start, 11 * mm, prefix)
    draw_google_wordmark(c, line_start + prefix_w + google_w / 2, 11 * mm, 12)

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(MUTED)
    c.drawCentredString(page_w / 2, 5.5 * mm, "Thank you for choosing NU Car Rentals")

    c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

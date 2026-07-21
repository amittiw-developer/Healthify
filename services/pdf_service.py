import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


W, H = A4
INK = colors.HexColor("#0f2233")
MUTED = colors.HexColor("#617089")
GREEN = colors.HexColor("#12a66a")
GREEN_DARK = colors.HexColor("#08784a")
LINE = colors.HexColor("#dfe8e4")
SOFT = colors.HexColor("#f7fbf9")
MINT = colors.HexColor("#eaf8f0")
AMBER_BG = colors.HexColor("#fff3dd")
AMBER = colors.HexColor("#c47b09")
RED_BG = colors.HexColor("#fff1f0")
RED = colors.HexColor("#b42318")


def has_text(value):
    return value is not None and str(value).strip() != ""


def has_list(value):
    return isinstance(value, list) and any(str(item).strip() for item in value)


def text(value, fallback="-"):
    return str(value).strip() if has_text(value) else fallback


def list_items(value):
    if not has_list(value):
        return ["No specific suggestion was generated."]
    return [str(item).strip() for item in value if str(item).strip()]


def wrap_lines(c, value, max_width, font="Helvetica", size=10):
    words = text(value, "").split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def draw_wrapped(c, value, x, y, max_width, font="Helvetica", size=10, color=INK, leading=14, max_lines=None):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap_lines(c, value, max_width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def ensure_page(c, y, needed=120):
    if y - needed > 78:
        return y
    draw_footer(c)
    c.showPage()
    return H - 54


def rounded_card(c, x, y, w, h, fill=colors.white, stroke=LINE, radius=10):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.roundRect(x, y - h, w, h, radius, stroke=1, fill=1)


def draw_footer(c):
    c.setStrokeColor(LINE)
    c.line(42, 50, W - 42, 50)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(42, 34, "HEALTHIFY")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(42, 23, "Checked and secured")
    c.drawRightString(W - 42, 34, "Authorized signature")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(W - 42, 23, "Amit Tiwari")


def draw_section(c, y, title, body=None, items=None, fill=colors.white, min_h=86):
    x = 42
    w = W - 84
    content_lines = []
    if body is not None:
        content_lines = wrap_lines(c, body, w - 36, "Helvetica", 10.5)
    if items is not None:
        for item in list_items(items):
            content_lines.extend(wrap_lines(c, f"- {item}", w - 36, "Helvetica", 10))
    h = max(min_h, 46 + len(content_lines) * 15)
    y = ensure_page(c, y, h + 20)
    rounded_card(c, x, y, w, h, fill=fill)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x + 16, y - 25, title)
    yy = y - 48
    if body is not None:
        yy = draw_wrapped(c, body, x + 16, yy, w - 32, "Helvetica", 10.5, colors.HexColor("#24384c"), 15)
    if items is not None:
        c.setFillColor(colors.HexColor("#24384c"))
        c.setFont("Helvetica", 10)
        for item in list_items(items):
            c.setFillColor(GREEN)
            c.circle(x + 20, yy + 4, 2.4, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#24384c"))
            for idx, line in enumerate(wrap_lines(c, item, w - 48, "Helvetica", 10)):
                c.drawString(x + 30, yy, line)
                yy -= 15
            yy -= 2
    return y - h - 12


def generate_pdf(report, STATIC_DIR):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Header
    logo_path = os.path.join(STATIC_DIR, "logo.png")
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 42, H - 82, width=34, height=34, mask="auto")
            brand_x = 84
        except Exception:
            brand_x = 42
    else:
        brand_x = 42
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(brand_x, H - 62, "Healthify")
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(brand_x, H - 78, "AI Health Awareness Report")

    rounded_card(c, W - 220, H - 42, 178, 70)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(W - 204, H - 65, "Report ID")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(W - 204, H - 82, text(report.get("report_id")))
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(W - 204, H - 101, text(report.get("date_time")))

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W / 2, H - 140, "Personal Health Insight")
    c.setFillColor(colors.HexColor("#4f6177"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 160, "Your personalized health overview and AI-powered recommendations.")

    y = H - 190
    y = draw_section(c, y, "What Healthify AI Understands", body=report.get("summary") or "Healthify could not prepare a clear summary from the shared details.", min_h=96)

    sev = text(report.get("severe"), "mild").lower()
    badge_fill, badge_text = (MINT, GREEN_DARK)
    if sev == "moderate":
        badge_fill, badge_text = AMBER_BG, AMBER
    elif sev == "high":
        badge_fill, badge_text = RED_BG, RED
    y = ensure_page(c, y, 86)
    rounded_card(c, 42, y, W - 84, 78)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(58, y - 25, "Current Priority")
    c.setFillColor(badge_fill)
    c.roundRect(58, y - 60, 90, 24, 12, stroke=0, fill=1)
    c.setFillColor(badge_text)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(103, y - 52, sev.title())
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(165, y - 45, "Use this as awareness guidance. Consult qualified care if symptoms worsen.")
    y -= 90

    y = ensure_page(c, y, 145)
    rounded_card(c, 42, y, W - 84, 132)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(58, y - 25, "Personal Details")
    details = [
        ("Name", report.get("name")), ("Age", report.get("age")), ("Gender", report.get("gender")), ("Location", report.get("location")),
        ("Weight", f"{report.get('weight')} kg" if has_text(report.get("weight")) else "-"), ("Height", f"{report.get('height_cm')} cm" if has_text(report.get("height_cm")) else "-"),
        ("Concern", report.get("concern_type")), ("Red Flag", report.get("red_flag") or "No"),
    ]
    cell_w = (W - 116) / 4
    start_y = y - 55
    for i, (label, value) in enumerate(details):
        col = i % 4
        row = i // 4
        xx = 58 + col * cell_w
        yy = start_y - row * 43
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawString(xx, yy, label)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.3)
        c.drawString(xx, yy - 14, text(value))
    y -= 144

    y = draw_section(c, y, "Care Recommendation", body=report.get("how_to_treat") or "Please share more detail so Healthify can prepare a clearer care recommendation.", fill=colors.HexColor("#f0fbf5"), min_h=92)
    y = draw_section(c, y, "Precautions", items=report.get("precautions"))
    y = draw_section(c, y, "Home Relief", items=report.get("home_relief"))
    y = draw_section(c, y, "Doctor Consultation", items=report.get("consultation"))
    y = draw_section(c, y, "Suggested Tests", items=report.get("blood_tests"))

    if has_text(report.get("thought")):
        y = draw_section(c, y, "Recovery Insight", body=report.get("thought"), fill=colors.HexColor("#fffaf0"), min_h=72)

    y = draw_section(
        c,
        y,
        "Health Awareness Notice",
        body="This AI-generated insight is for health awareness only. It is not a diagnosis, prescription, emergency service, or replacement for qualified medical care.",
        fill=colors.HexColor("#fff7f6"),
        min_h=76,
    )
    y = ensure_page(c, y, 75)
    c.setFillColor(MINT)
    c.roundRect(42, y - 42, W - 84, 34, 10, stroke=0, fill=1)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, y - 29, "Your health data is encrypted and secure with Healthify.")

    draw_footer(c)
    c.save()
    buffer.seek(0)
    return buffer

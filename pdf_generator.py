import io
import os
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from PIL import Image

# pdf_generator.py
# Creates a multi-page PDF with title page, content sections, and images.


def _draw_wrapped_text(c, text, x, y, max_width, leading=14):
    """Simple word-wrap for ReportLab canvas text."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if stringWidth(test, "Helvetica", 12) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def generate_pdf(topic: str, content: Dict, image_paths: List[str]) -> bytes:
    """
    Generate a PDF bytes buffer from topic, structured content, and image list.

    `content` is expected to have keys: story (str), steps (list), summary (str), key_points (list)
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title page
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 6 * cm, topic)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 7 * cm, "StoryLearn AI — Learning through story-style explanations")
    c.showPage()

    # Story section
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, height - 2 * cm, "Story Explanation")
    c.setFont("Helvetica", 12)
    y = height - 3 * cm
    y = _draw_wrapped_text(c, content.get("story", ""), 2 * cm, y, max_width=width - 4 * cm)

    # Insert images (if any) spaced between content
    for img_path in image_paths:
        try:
            img = Image.open(img_path)
            img_w, img_h = img.size
            aspect = img_h / img_w
            # fit to page width
            display_w = width - 4 * cm
            display_h = display_w * aspect
            if y - display_h < 2 * cm:
                c.showPage()
                y = height - 2 * cm
            c.drawInlineImage(img_path, 2 * cm, y - display_h, width=display_w, height=display_h)
            y = y - display_h - 1 * cm
        except Exception:
            continue

    # Steps
    if content.get("steps"):
        c.showPage()
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, height - 2 * cm, "Step-by-step Concept Flow")
        c.setFont("Helvetica", 12)
        y = height - 3 * cm
        for i, s in enumerate(content.get("steps", []), start=1):
            y = _draw_wrapped_text(c, f"{i}. {s}", 2 * cm, y, max_width=width - 4 * cm)
            if y < 3 * cm:
                c.showPage()
                y = height - 2 * cm

    # Summary and key points
    c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, height - 2 * cm, "Summary")
    c.setFont("Helvetica", 12)
    y = height - 3 * cm
    y = _draw_wrapped_text(c, content.get("summary", ""), 2 * cm, y, max_width=width - 4 * cm)

    if content.get("key_points"):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, y - 1 * cm, "Key Points")
        y -= 1.5 * cm
        c.setFont("Helvetica", 12)
        for kp in content.get("key_points", []):
            y = _draw_wrapped_text(c, f"- {kp}", 2 * cm, y, max_width=width - 4 * cm)
            if y < 3 * cm:
                c.showPage()
                y = height - 2 * cm

    c.save()
    buffer.seek(0)
    return buffer.read()

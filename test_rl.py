from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

font_path = "NanumGothic.ttf"
output = "test_rl.pdf"

try:
    c = canvas.Canvas(output)
    pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
    c.setFont('NanumGothic', 20)
    c.drawString(100, 700, "Hello World")
    c.drawString(100, 650, "안녕하세요 세계")
    c.save()
    print("Created test_rl.pdf")
except Exception as e:
    print(f"Error: {e}")

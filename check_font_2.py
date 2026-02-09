from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Font exists: {os.path.exists('NanumGothic.ttf')}")
try:
    font = TTFont('TestFont', 'NanumGothic.ttf')
    pdfmetrics.registerFont(font)
    print("Font OK")
except Exception as e:
    print(f"Font FAIL: {e}")
    sys.exit(1)

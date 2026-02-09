from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def test_font(font_name, font_file, output_filename):
    print(f"Testing {font_name} from {font_file}...")
    
    # Register font
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_file))
    except Exception as e:
        print(f"Failed to register font: {e}")
        return

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            body {{
                font-family: '{font_name}';
                font-size: 20pt;
            }}
        </style>
    </head>
    <body>
        <h1>Font Test: {font_name}</h1>
        <p>English: Hello World</p>
        <p>Korean: 안녕하세요 세계</p>
        <p>Numbers: 1234567890</p>
    </body>
    </html>
    """

    with open(output_filename, "wb") as f:
        pisa_status = pisa.CreatePDF(html_content, dest=f, encoding='utf-8')

    if pisa_status.err:
        print("Error during PDF creation")
    else:
        print(f"Created {output_filename}")

if __name__ == "__main__":
    # Test NanumGothic
    if os.path.exists("NanumGothic.ttf"):
        test_font("NanumGothic", "NanumGothic.ttf", "debug_nanum.pdf")
    
    # Test Malgun
    if os.path.exists("malgun.ttf"):
        test_font("MalgunGothic", "malgun.ttf", "debug_malgun.pdf")

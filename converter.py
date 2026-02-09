import sys
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def convert_markdown_to_pdf(input_md_path, output_pdf_path):
    # 1. Register Font
    font_path = resource_path("NanumGothic.ttf")
    if not os.path.exists(font_path):
        # Fallback to absolute path or local check
        font_path = os.path.abspath("NanumGothic.ttf")
    
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font {font_path} not found.")

    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', font_path)) 
    except Exception as e:
        raise RuntimeError(f"Font registration error: {e}")

    # 2. Define Styles with Korean Font
    styles = getSampleStyleSheet()
    
    # Update Normal style
    styles['Normal'].fontName = 'NanumGothic'
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 16
    styles['Normal'].alignment = TA_LEFT

    # Create Custom Styles
    style_h1 = ParagraphStyle(
        'Heading1_Korean', 
        parent=styles['Heading1'], 
        fontName='NanumGothic', 
        fontSize=24, 
        leading=30, 
        spaceAfter=12,
        textColor=colors.black
    )
    style_h2 = ParagraphStyle(
        'Heading2_Korean', 
        parent=styles['Heading2'], 
        fontName='NanumGothic', 
        fontSize=18, 
        leading=22, 
        spaceAfter=10,
        textColor=colors.black
    )
    style_h3 = ParagraphStyle(
        'Heading3_Korean', 
        parent=styles['Heading3'], 
        fontName='NanumGothic', 
        fontSize=14, 
        leading=18, 
        spaceAfter=8,
        textColor=colors.black
    )
    style_code = ParagraphStyle(
        'Code_Korean',
        fontName='NanumGothic', # Ideally Monospace, but usually need a Korean Mono. NanumGothic works for readability.
        fontSize=9,
        leading=12,
        textColor=colors.darkblue,
        backColor=colors.whitesmoke,
        borderPadding=5
    )
    style_list_item = ParagraphStyle(
        'ListItem_Korean',
        parent=styles['Normal'],
        fontName='NanumGothic',
        leftIndent=15
    )

    # 3. Read File
    with open(input_md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 4. Parse & Build Story
    story = []
    
    in_code_block = False
    code_lines = []

    for line in lines:
        line = line.rstrip() # keep indentation? ReportLab Pre formatted needs it. 
        # But for non-code, strip line break
        
        # Code Block Handling
        if line.strip().startswith("```"):
            if in_code_block:
                # End block
                full_code = "\n".join(code_lines)
                # Escape generic XML characters for ReportLab
                full_code = full_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Preformatted(full_code, style_code))
                story.append(Spacer(1, 12))
                in_code_block = False
                code_lines = []
            else:
                # Start block
                in_code_block = True
            continue
        
        if in_code_block:
            code_lines.append(line)
            continue

        # Normal Markdown Parsing
        line_strip = line.strip()
        if not line_strip:
            continue

        # Simple Bold/Italic Parsing for ReportLab tags
        # **text** -> <b>text</b>
        # *text* -> <i>text</i> [But we don't have Italic font registered, so skip or map to Bold]
        # ReportLab supports <b> tag if font has B variant (we mapped Regular to Bold name, so it "works" visually as same weight or synthetic bold if supported)
        
        # Replace **...** with <b>...</b>
        line_strip = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_strip)
        # Replace `...` with <font color="red">...</font>
        line_strip = re.sub(r'`(.*?)`', r'<font color="darkred">\1</font>', line_strip)

        if line_strip.startswith("# "):
            story.append(Paragraph(line_strip[2:], style_h1))
            story.append(Spacer(1, 12))
        elif line_strip.startswith("## "):
            story.append(Paragraph(line_strip[3:], style_h2))
            story.append(Spacer(1, 10))
        elif line_strip.startswith("### "):
            story.append(Paragraph(line_strip[4:], style_h3))
            story.append(Spacer(1, 8))
        elif line_strip.startswith("- ") or line_strip.startswith("* "):
            # Bullet list
            text = line_strip[2:]
            story.append(ListFlowable([
                ListItem(Paragraph(text, style_list_item), bulletColor=colors.black, value='circle')
            ], bulletType='bullet', start='circle'))
        elif line_strip.strip() == "---" or line_strip.strip() == "***":
             story.append(Spacer(1, 12)) 
             # Draw line? using drawing, but Spacer is fine for now
        else:
            # Normal Paragraph
            # Handle links [text](url) -> <link href="url">text</link>
            line_strip = re.sub(r'\[(.*?)\]\((.*?)\)', r'<link href="\2" color="blue"><u>\1</u></link>', line_strip)
            story.append(Paragraph(line_strip, styles['Normal']))
            story.append(Spacer(1, 6))

    # 5. Build PDF
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )
    
    print(f"Building PDF: {output_pdf_path}")
    doc.build(story)
    print("Success.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.md> [output.pdf]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(input_file)[0] + ".pdf"
    
    convert_markdown_to_pdf(input_file, output_file)

from PIL import Image, ImageDraw, ImageFont

def create_m_to_p_icon():
    # Make a square icon
    size = (256, 256)
    bg_color = (0, 122, 255) # A nice blue
    text_color = (255, 255, 255) # White
    
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Text "M to P"
    text = "M to P"
    
    try:
        # Try to find a nice font, or fallback to default
        font_path = "malgunbd.ttf" # Use malgun bold if available
        font = ImageFont.truetype(font_path, 80)
    except:
        font = ImageFont.load_default()

    # Calculate text position to center it
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        w = right - left
        h = bottom - top
    except AttributeError:
        w, h = draw.textsize(text, font=font)
        
    x = (size[0] - w) / 2
    y = (size[1] - h) / 2
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Save as .ico
    img.save("icon.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Created icon.ico with text 'M to P'")

if __name__ == "__main__":
    create_m_to_p_icon()

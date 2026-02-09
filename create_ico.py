from PIL import Image
import os

def create_ico(png_path, ico_path):
    try:
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Resize/Crop to square
        width, height = img.size
        new_size = min(width, height)
        
        left = (width - new_size) / 2
        top = (height - new_size) / 2
        right = (width + new_size) / 2
        bottom = (height + new_size) / 2

        img = img.crop((left, top, right, bottom))
        
        # Resize to common icon sizes
        icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        img.save(ico_path, sizes=icon_sizes)
        print(f"Successfully created {ico_path}")
    except Exception as e:
        print(f"Error creating ICO: {e}")

if __name__ == "__main__":
    source_file = None
    if os.path.exists("icon.png"):
        source_file = "icon.png"
    elif os.path.exists("app_icon.png"):
        source_file = "app_icon.png"
        
    if source_file:
        print(f"Found {source_file}, converting to icon.ico...")
        create_ico(source_file, "icon.ico")
    else:
        print("No source image (icon.png or app_icon.png) found.")

from PIL import Image, ImageDraw, ImageFont
import textwrap
from meme_config import meme_template_db

def draw_centered_text(draw, text, config, font):
    """
    Helper function to wrap text and center it in the box.
    """
    x, y = config['pos']
    w, h = config['box_size']
    
    # 1. Wrap text (break long lines)
    # Width=15 is a guess. Adjust based on font size.
    lines = textwrap.wrap(text, width=15) 
    
    # 2. Calculate total height
    bbox = draw.textbbox((0, 0), "A", font=font)
    line_height = bbox[3] - bbox[1] + 10 # 10px padding
    total_height = len(lines) * line_height
    
    # 3. Find starting Y to center vertically
    current_y = y + (h - total_height) // 2
    
    # 4. Draw each line
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        center_x = x + (w - line_w) // 2
        
        draw.text((center_x, current_y), line, font=font, fill=config['color'])
        current_y += line_height

def build_meme(roast_data):
    """
    Takes the JSON from the Brain and creates the image.
    """
    # 👇 LOAD THE SPECIFIC CONFIG
    # Make sure 'drake_meme' matches the key in your meme_config.py
    drake_config = meme_template_db['drake_meme']
    
    # 1. Load Template
    try:
        # We use convert("RGBA") to handle transparency correctly
        img = Image.open(drake_config['filename']).convert("RGBA")
    except FileNotFoundError:
        print(f"❌ Error: Could not find {drake_config['filename']}")
        return None
        
    draw = ImageDraw.Draw(img)
    
    # 2. Load Font
    # Try to load a nice font, fallback to default if missing
    try:
        # Use the font size defined in your config
        font_size = drake_config['top_text']['font_size']
        font = ImageFont.truetype("Arial.ttf", font_size)
    except OSError:
        print("⚠️ Warning: Arial.ttf not found. Using default font (it might be small).")
        font = ImageFont.load_default()

    # 3. Draw Top Text ("No")
    print(f"🎨 Drawing Top Text: {roast_data['top_text']}")
    draw_centered_text(draw, roast_data['top_text'], drake_config['top_text'], font)
    
    # 4. Draw Bottom Text ("Yes")
    print(f"🎨 Drawing Bottom Text: {roast_data['bot_text']}")
    draw_centered_text(draw, roast_data['bot_text'], drake_config['bot_text'], font)
    
    # 5. Save the result
    output_filename = "final_meme.png"
    img.save(output_filename)
    print(f"✅ Meme Saved as {output_filename}")
    return output_filename
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 👇 CORRECT IMPORT NAME
from meme_config import meme_template_db 

def draw_centered_text(draw, text, config, font):
    """
    Helper function to wrap text and center it in the box.
    """
    # 1. SAFETY CHECK
    if config['color'] is None or config['color'] == "transparent":
        return

    x, y = config['pos']
    w, h = config['box_size']
    
    # --- DYNAMIC WRAPPING MATH ---
    # We estimate how many characters fit in one line.
    # A standard character is roughly 0.6 times the font size in width.
    avg_char_width = config['font_size'] * 0.6
    max_chars_per_line = int(w / avg_char_width)
    
    # Wrap text based on the calculated width (e.g., Drake=15, DiCaprio=35)
    lines = textwrap.wrap(text, width=max_chars_per_line) 
    # -----------------------------
    
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
    Constructs the meme based on the roast data and template selected.
    """
    # 1. Get the template key selected by the AI (default to drake if missing)
    template_key = roast_data.get("template", "drake_meme") 
    
    # 2. Safety Check: Does this key exist in your DB?
    if template_key not in meme_template_db:
        print(f"❌ Error: Template '{template_key}' not found in meme_config.py!")
        # Fallback logic
        if "drake_meme" in meme_template_db:
            print("⚠️ Switching to default 'drake_meme'...")
            template_key = "drake_meme"
        else:
            return None
            
    # 3. Load the actual config DICTIONARY
    # This is the critical fix: we use the key to get the dict
    meme_config = meme_template_db[template_key]
    
    print(f"🎨 Using Template: {template_key}")

    # 4. Load Template Image
    try:
        # Use meme_config['filename'], NOT template_key['filename']
        img = Image.open(meme_config['filename']).convert("RGBA")
    except FileNotFoundError:
        print(f"❌ Error: Could not find image file at: {meme_config['filename']}")
        return None
        
    draw = ImageDraw.Draw(img)
    
    # 5. Load Font
    try:
        font_size = meme_config['top_text']['font_size']
        font = ImageFont.truetype("Arial.ttf", font_size)
    except OSError:
        print("⚠️ Warning: Arial.ttf not found. Using default font.")
        font = ImageFont.load_default()

    # 6. Draw Top Text
    if 'top_text' in meme_config and 'top_text' in roast_data:
        print(f"🎨 Drawing Top Text: {roast_data['top_text']}")
        draw_centered_text(draw, roast_data['top_text'], meme_config['top_text'], font)
    
    # 7. Draw Bottom Text
    if 'bot_text' in meme_config and 'bot_text' in roast_data:
        print(f"🎨 Drawing Bottom Text: {roast_data['bot_text']}")
        draw_centered_text(draw, roast_data['bot_text'], meme_config['bot_text'], font)
    
    # 8. Save the result
    output_filename = "final_meme.png"
    img.save(output_filename)
    print(f"✅ Meme Saved as {output_filename}")
    return output_filename
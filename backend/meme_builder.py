from PIL import Image, ImageDraw, ImageFont
import textwrap
from meme_config import meme_template_db

def fit_text_to_box(draw, text, box_w, box_h, font_path, max_font_size=80):
    """
    Dynamically finds the largest font size that fits the text inside the box.
    """
    size = max_font_size
    min_size = 20
    
    while size >= min_size:
        try:
            font = ImageFont.truetype(font_path, size)
        except OSError:
            font = ImageFont.load_default()
            return font, textwrap.wrap(text, width=20) 

        avg_char_width = size * 0.5
        chars_per_line = max(1, int(box_w / avg_char_width))
        lines = textwrap.wrap(text, width=chars_per_line)
        
        bbox = draw.textbbox((0, 0), "Aj", font=font)
        line_height = bbox[3] - bbox[1] + 5
        total_text_h = len(lines) * line_height
        
        if total_text_h <= box_h:
            return font, lines
            
        size -= 4  # Shrink and retry
        
    return ImageFont.load_default(), textwrap.wrap(text, width=20)

def build_meme(roast_data):
    # 1. Select Template
    template_key = roast_data.get("template", "drake_meme")
    if template_key not in meme_template_db:
        # Fallback to first available key
        keys = list(meme_template_db.keys())
        if keys: template_key = keys[0]
        else: return None

    config = meme_template_db[template_key]
    print(f"🎨 Using Template: {template_key}")

    # 2. Load Image
    try:
        img = Image.open(config['filename']).convert("RGBA")
    except FileNotFoundError:
        print(f"❌ Error: Missing file {config['filename']}")
        return None
        
    draw = ImageDraw.Draw(img)
    font_path = "Arial.ttf" 

    # 3. UNIVERSAL LOOP (Handles Top/Bot AND Text_1/2/3/4)
    for key, text_config in config.items():
        if key == "filename": continue  # Skip the filename string
        
        # Check if AI provided text for this key (e.g. 'text_1')
        if key not in roast_data: continue

        text = str(roast_data[key]).upper()
        
        # Skip if color is None (like in DiCaprio bot_text)
        if text_config.get('color') is None: continue

        # Calculate layout
        x, y = text_config['pos']
        w, h = text_config['box_size']
        
        # Auto-size font
        font, lines = fit_text_to_box(draw, text, w, h, font_path, text_config.get('font_size', 60))
        
        # Center Vertically
        bbox = draw.textbbox((0, 0), "Aj", font=font)
        line_height = bbox[3] - bbox[1] + 5
        total_h = len(lines) * line_height
        current_y = y + (h - total_h) // 2
        
        # Draw Lines
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_w = line_bbox[2] - line_bbox[0]
            center_x = x + (w - line_w) // 2
            
            draw.text((center_x, current_y), line, font=font, fill=text_config['color'])
            current_y += line_height

    output_filename = "final_meme.png"
    img.save(output_filename)
    return output_filename
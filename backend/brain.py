import os
import base64
import json
import random
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI

# Import config
try:
    from meme_config import meme_template_db as TEMPLATE_DB
except ImportError:
    TEMPLATE_DB = {}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path: str) -> str:
    path = Path(image_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_meme_roast(image_path: str, roast_level: str = "medium", max_tokens: int = 3000) -> Dict[str, Any]:
    
    # 1. Setup available memes
    available_memes = list(TEMPLATE_DB.keys())
    memes_list_str = ", ".join(available_memes)

    # 2. Encode Image
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError as e:
        return {"error": str(e)}

    print(f"🧠 AI Analyzing vibe... (Level: {roast_level})")

    # 3. Define Persona
    instructions = {
        "mild": "You are a playful TA. Tease them about simple syntax errors.",
        "medium": "You are a tired Senior Dev. Be sarcastic about their spaghetti code.",
        "savage": "You are a toxic Tech Lead. Destroy their ego. Mock their unemployment."
    }
    persona = instructions.get(roast_level.lower(), instructions["medium"])

    # 4. THE CORE DIRECTIVE (Your Requested Prompt)
    system_prompt = (
        f"{persona}\n\n"
        "Turn this image into a brutally savage meme roasting a CS student.\n"
        "Theme: jobless, homeless, unemployed coder, broke student energy.\n"
        "Use dark humor, tech jokes, and brutal sarcasm.\n"
        "Keep captions short, lethal, and viral.\n\n"
        f"AVAILABLE TEMPLATES: [{memes_list_str}]\n"
        "RULES FOR JSON OUTPUT:\n"
        "1. 'drake_meme' / 'panda_suit': Return JSON with keys 'top_text' and 'bot_text'.\n"
        "2. 'dicaprio_laugh': Return JSON with 'top_text' (setup) and 'bot_text' (punchline).\n"
        "3. 'clown_makeup': Return JSON with 'text_1', 'text_2', 'text_3', 'text_4'.\n"
        "   - Step 1: Normal thought (e.g. 'I will apply to FAANG')\n"
        "   - Step 2: Optimistic mistake (e.g. 'I will learn Rust in a weekend')\n"
        "   - Step 3: Delusion (e.g. 'Who needs a degree?')\n"
        "   - Step 4: Full Clown (e.g. 'Unpaid internship at 30')\n\n"
        "JSON ONLY. NO EXPLANATION."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": f"Roast this person. Level: {roast_level}."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Validation: If AI picks a fake template, force a random real one
        if result.get("template") not in TEMPLATE_DB:
            result["template"] = random.choice(available_memes)
            
        return result

    except Exception as e:
        return {"error": f"Brain Freeze: {str(e)}"}

# Wrapper
def get_roast(image_path, roast_level="medium"):
    return generate_meme_roast(image_path, roast_level)
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

def generate_meme_roast(
    image_path: str,
    roast_level: str = "medium",
    max_tokens: int = 3000
) -> Dict[str, Any]:
    
    # 1. SELECT TEMPLATE
    available_memes = list(TEMPLATE_DB.keys())
    if not available_memes:
        return {"error": "No templates found in config."}
    
    selected_template = random.choice(available_memes)
    print(f"🎲 Template: {selected_template}")

    # 2. DEFINE TECHNICAL OVERRIDES
    # Your text asks for "Only 2 captions", but some memes need 4 or 5.
    # We append this logic at the end to ensure the code doesn't break.
    technical_override = ""
    
    if selected_template == "brain_explode":
        technical_override = (
            f"\n\n--- ⚠️ TEMPLATE OVERRIDE: {selected_template} ---\n"
            "Ignore the '2 captions' limit above. This is a 4-PANEL meme.\n"
            "You MUST return 4 keys: 'text_1', 'text_2', 'text_3', 'text_4'.\n"
            "Logic: Smart -> Complicated -> Stupid -> Galaxy Brain."
        )
    elif selected_template == "clown_makeup":
        technical_override = (
            f"\n\n--- ⚠️ TEMPLATE OVERRIDE: {selected_template} ---\n"
            "Ignore the '2 captions' limit above. This is a 4-PANEL meme.\n"
            "You MUST return 4 keys: 'text_1', 'text_2', 'text_3', 'text_4'.\n"
            "Logic: Confidence -> Doubt -> Mistake -> Full Clown."
        )
    elif selected_template == "ballon_scared":
        technical_override = (
            f"\n\n--- ⚠️ TEMPLATE OVERRIDE: {selected_template} ---\n"
            "Ignore the '2 captions' limit above. This is a 5-TEXT meme.\n"
            "You MUST return 5 keys: 'text_5' (The Monster), 'text_1', 'text_2', 'text_3', 'text_4' (The Victim)."
        )
    else:
        technical_override = (
            f"\n\n--- TEMPLATE INFO: {selected_template} ---\n"
            "Adhere to the 2-caption rule above.\n"
            "Return keys: 'top_text' and 'bot_text'."
        )

    # 3. YOUR EXACT SYSTEM PROMPT
    # We paste your text exactly as requested.
    user_persona_text = (
        "You are a savage, chaotic Gen Z meme creator who makes bold, embarrassing, viral roast captions."
        "\n\nYour job is to roast and stereotype the person in the image in a funny, exaggerated, meme-style way. The goal is to judge their appearance, facial expression, and clothing FIRST, then connect that to a relatable computer science stereotype.\n\nThe humor should feel like:\n\n• Group chat roasting\n• TikTok comments\n• Twitter threads\n• Internet meme chaos\n\nThe tone must be confident, judgmental, and savage.\n\n---\n\nCRITICAL RULE (MOST IMPORTANT)\n\nYou MUST ALWAYS comment on the person’s appearance.\n\nThis is NOT optional.\n\nEvery caption MUST include at least ONE of the following:\n\n• Facial expression\n• Clothing or fashion\n• Body language or pose\n• Overall vibe or energy\n\nIf you do not comment on the person’s appearance, your response is wrong.\n\nNever skip this.\n\n---\n\nMANDATORY STRUCTURE\n\nStep 1: Judge the person’s appearance first.\nStep 2: Make a bold assumption about their personality or habits.\nStep 3: Connect it to a simple computer science stereotype.\n\nAll captions must follow this structure.\n\n---\n\nWHAT TO NOTICE ABOUT THE PERSON\n\nFocus on:\n\n• Confused, tired, smug, awkward, or overconfident expressions\n• Weird, outdated, or trying-too-hard fashion\n• Lazy or chaotic body language\n• Clueless or stressed vibe\n• Fake confidence or fake intelligence\n• Low effort or messy energy\n\nMake very strong assumptions based on how they look.\n\n---\n\nCOMPUTER SCIENCE STEREOTYPES (SIMPLE ONLY)\n\nAlways connect the roast to relatable CS stereotypes such as:\n\n• Copying from Stack Overflow\n• Watching tutorials but never coding\n• Fake productivity\n• Coffee addiction\n• Debugging all night\n• Gaming instead of studying\n• Broken sleep schedule\n• Using ChatGPT for everything\n• \"It works on my machine\"\n• Last-minute cramming\n• Never touching grass\n\nDo NOT use advanced or niche tech topics.\n\n---\n\nROAST LEVELS\n\nHigh\nSavage and embarrassing.\n\nVery High\nMore humiliating and exaggerated.\n\nUnhinged\nMaximum chaos and wild assumptions.\n\nNever ever ever be soft.\n\n---\n\nBEHAVIOR RULES\n\n• No polite or neutral descriptions.\n• No explaining the joke.\n• No long sentences.\n• No formal language.\n• No emojis.\n• Be bold and confident.\n• Make strong assumptions.\n\n---\n\nIF NO PERSON IS VISIBLE\n\nIf the image does not clearly show a person, create a funny assumption about the person behind the image and still connect it to a tech stereotype.\n\nExample:\nBro took this picture after breaking production.\n\nNever say there is no person. Always assume someone is behind it.\n\n---\n\nOUTPUT FORMAT (STRICT)\n\nReturn ONLY 2 captions.\n\nEach caption must:\n\n• Be under 10 words\n• Be on separate lines\n• Match the selected meme format\n• Reflect the selected roast level\n• No numbering\n• No extra text\n• No explanation"
    )

    # Combine them (Your Text + Technical Fixes + JSON Requirement)
    system_prompt = (
        f"{user_persona_text}"
        f"{technical_override}"
        "\n\nFINALLY: Return valid JSON only. Key 'visual_roast' is optional but good for logging."
    )

    try:
        base64_image = encode_image(image_path)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Roast this photo based on visuals. JSON only."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # --- SANITIZATION ---
        result["user_image_path"] = image_path
        
        # Force correct template
        if result.get("template") not in TEMPLATE_DB:
             result["template"] = selected_template

        if "visual_roast" in result:
            print(f"🔥 VISUAL ROAST: {result['visual_roast']}")

        # KEY MAPPING (To ensure builder compatibility)
        if selected_template in ["clown_makeup", "brain_explode"]:
            if "text_1" not in result:
                result["text_1"] = result.get("top_text", "Look 1")
                result["text_2"] = result.get("bot_text", "Look 2")
                result["text_3"] = "Look 3"
                result["text_4"] = "Look 4"
        elif selected_template == "ballon_scared":
             if "text_5" not in result:
                result["text_1"] = "Me"
                result["text_2"] = "My Dignity"
                result["text_3"] = "My Style"
                result["text_4"] = "My Future"
                result["text_5"] = "This Photo"
        else: 
            if "top_text" not in result:
                result["top_text"] = result.get("text_1", "Expectation")
                result["bot_text"] = result.get("text_2", "Reality")

        return result

    except Exception as e:
        print(f"❌ BRAIN ERROR: {str(e)}")
        return {"error": f"Brain Freeze: {str(e)}"}

def get_roast(image_path, roast_level="medium"):
    return generate_meme_roast(image_path, roast_level)
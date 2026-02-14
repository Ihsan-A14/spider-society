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
    """Encodes a local image to base64 for the API."""
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
    
    # 1. Get available memes
    available_memes = list(TEMPLATE_DB.keys())
    memes_list_str = ", ".join(available_memes)

    # 2. Encode Image
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError as e:
        return {"error": str(e)}

    print(f"🧠 DevRoast Analyzing... (Level: {roast_level})")

    # 3. THE DEVROAST SYSTEM PROMPT
    system_prompt = (
        "You are 'DevRoast,' a cynical, hilarious, and culturally aware meme generator for Computer Science students.\n"
        "Your goal: Generate a 'savage' meme based on the user's photo.\n\n"
        
        "--- ANALYSIS GUIDELINES ---\n"
        "1. CLOTHING: Suit (Desperate), Hoodie (Grinder), Smart Casual (Fake Intern).\n"
        "2. EXPRESSION: Smile (Ignorant), Sad (Segfault), Confused (Vim).\n"
        "3. TONE: Savage but lighthearted CS jokes.\n\n"

        "--- MEME LOGIC ENGINE (CRITICAL) ---\n"
        "You MUST follow the specific format for the chosen template:\n\n"
        
        "1. **brain_explode** (4 panels): PROGRESSION of Intelligence/Stupidity.\n"
        "   - text_1: The normal/correct way (e.g. 'Using Python loops')\n"
        "   - text_2: The complex way (e.g. 'Using List Comprehensions')\n"
        "   - text_3: The bad way (e.g. 'Recursion with no exit condition')\n"
        "   - text_4: The ABSURD way (e.g. 'Hardcoding 1000 print statements')\n\n"
        
        "2. **clown_makeup** (4 panels): PROGRESSION of Delusion.\n"
        "   - text_1: Normal thought (e.g. 'I'll finish this side project')\n"
        "   - text_2: Optimistic mistake (e.g. 'I don't need Git, I'll be careful')\n"
        "   - text_3: Delusion (e.g. 'I can write my own database')\n"
        "   - text_4: Full Clown (e.g. 'Lost all data, no backups')\n\n"
        
        "3. **ballon_scared** (5 texts): The CHASE.\n"
        "   - text_5: The Monster/Threat (e.g. 'The Senior Dev', 'Segfault')\n"
        "   - text_1, text_2, text_3, text_4: The Victim running away (e.g. 'Me', 'My Code', 'My Career', 'My Sanity')\n\n"
        
        "4. **drake_meme** / **panda_suit** (2 panels): REJECTION vs ACCEPTANCE.\n"
        "   - top_text: The 'Good' practice that you reject (e.g. 'Writing Unit Tests')\n"
        "   - bot_text: The 'Bad' habit you actually do (e.g. 'Testing in Production')\n\n"

        "5. **dicaprio_laugh** (2 texts): MOCKERY.\n"
        "   - top_text: The Setup (e.g. 'He thinks HTML is a programming language')\n"
        "   - bot_text: The Punchline (e.g. 'Wait until he sees CSS')\n\n"

        "--- OUTPUT FORMAT (STRICT JSON) ---\n"
        f"Choose the BEST template from: [{memes_list_str}].\n"
        "Output strictly valid JSON:\n"
        "{\n"
        "  'visual_roast': 'Savage comment on their look',\n"
        "  'template': 'template_key',\n"
        "  'text_1': '...',\n"
        "  'text_2': '...',\n"
        "  'text_3': '...',\n"
        "  'text_4': '...',\n"
        "  'text_5': '...',\n"
        "  'top_text': '...',\n"
        "  'bot_text': '...'\n"
        "}\n"
        "Use ONLY the keys relevant to the chosen template."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Analyze this dev. JSON only."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # --- DATA SANITIZATION ---
        result["user_image_path"] = image_path
        
        if "visual_roast" in result:
            print(f"🔥 VISUAL ROAST: {result['visual_roast']}")

        if result.get("template") not in TEMPLATE_DB:
            print(f"⚠️ Invalid template '{result.get('template')}'. Defaulting to drake_meme.")
            result["template"] = "drake_meme"

        template = result["template"]
        
        # FIX MISSING KEYS / FORMATTING
        if template == "brain_explode":
            if "text_1" not in result:
                result["text_1"] = "Writing Code"
                result["text_2"] = "StackOverflow"
                result["text_3"] = "ChatGPT"
                result["text_4"] = "Random Guessing"

        elif template == "clown_makeup":
             if "text_1" not in result:
                # Map standard top/bot if AI failed
                result["text_1"] = result.get("top_text", "Using a Library")
                result["text_2"] = result.get("bot_text", "Writing it yourself")
                result["text_3"] = "Writing it in Assembly"
                result["text_4"] = "Coding on a whiteboard"
        
        elif template == "ballon_scared":
             if "text_5" not in result:
                result["text_1"] = "Me"
                result["text_2"] = "Code"
                result["text_3"] = "Bugs"
                result["text_4"] = "Deadline"
                result["text_5"] = "The P1 Ticket"

        else: # Standard 2-panel memes
            if "top_text" not in result:
                result["top_text"] = result.get("text_1", "404 Text Not Found")
                result["bot_text"] = result.get("text_2", "Try again")

        return result

    except Exception as e:
        print(f"❌ BRAIN ERROR: {str(e)}")
        return {"error": f"Brain Freeze: {str(e)}"}

def get_roast(image_path, roast_level="medium"):
    return generate_meme_roast(image_path, roast_level)
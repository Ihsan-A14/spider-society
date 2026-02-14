import os
import base64
import json
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI

# Import your config
try:
    from meme_config import meme_template_db
except ImportError:
    # Fallback for testing if config is missing
    meme_template_db = {"drake_meme": {}} 

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
    
    # 1. Get available memes dynamically from your config
    available_memes = list(meme_template_db.keys())
    memes_list_str = ", ".join(available_memes)

    # 2. Encode Image
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError as e:
        return {"error": str(e)}

    print(f"🧠 AI Analyzing vibe... (Level: {roast_level} | Memes: {len(available_memes)})")

    # 3. Define the CS Persona
    # This dictionary controls the "heat" of the roast
    instructions = {
        "mild": "You are a helpful TA. Tease them gently about simple errors (syntax, missing semicolons).",
        "medium": "You are a tired Senior Dev. Be sarcastic about their code quality, spaghetti logic, and bad git habits.",
        "savage": "You are a ruthless StackOverflow moderator. Destroy their ego. Mock their existence. Focus on unemployment, AI replacing them, and their bad 'vibe'."
    }
    persona = instructions.get(roast_level.lower(), instructions["medium"])

    system_prompt = (
        f"{persona}\n"
        "TASK: Analyze the user's selfie and generate a roast meme.\n"
        "THEME: Computer Science, Coding, CS Majors, CS Unemployment, Hackathons, Tech Life.\n\n"
        f"AVAILABLE TEMPLATES: [{memes_list_str}]\n"
        "1. Select the BEST template from the list that fits the user's vibe.\n"
        "   - 'drake_meme': Good for Rejection/Acceptance.\n"
        "   - 'panda_suit': Good for 'Trashy Reality' vs 'Professional Lie'.\n"
        "   - 'dicaprio_laugh': Good for condescending mockery.\n"
        "2. OUTPUT strict JSON:\n"
        "   {\n"
        "     'template': 'one_of_the_keys_above',\n"
        "     'top_text': 'Text for the top box',\n"
        "     'bot_text': 'Text for the bottom box'\n"
        "   }\n"
        "Constraint: Keep text under 12 words."
    )

    # 4. Call GPT-5-Mini
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": f"Roast this CS major. Level: {roast_level}."},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Verify the AI chose a valid template
        if result.get("template") not in meme_template_db:
            print(f"⚠️ AI chose invalid template '{result.get('template')}'. Defaulting to drake_meme.")
            result["template"] = "drake_meme"
            
        return result

    except Exception as e:
        return {"error": f"Brain Freeze: {str(e)}"}

# Wrapper for backward compatibility
def get_roast(image_path, roast_level="medium"):
    return generate_meme_roast(image_path, roast_level)
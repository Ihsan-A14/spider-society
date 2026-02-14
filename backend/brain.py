import os
import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI

# ----------------------------------------------------------------------
# API Key Handling
# ----------------------------------------------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set. Check your terminal environment variables.")

client = OpenAI(api_key=api_key)

# Import the template database from your config file
from meme_config import meme_template_db # Changed from meme_template_db to match your config file name usually

# ----------------------------------------------------------------------
# Helper: encode image to base64
# ----------------------------------------------------------------------
def encode_image(image_path: str) -> str:
    path = Path(image_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ----------------------------------------------------------------------
# Core function: generate roast
# ----------------------------------------------------------------------
def generate_meme_roast(
    image_path: str,
    detail: str = "low",
    max_tokens: int = 3000
) -> Dict[str, Any]:
    
    # Encode the image
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError as e:
        return {"error": str(e)}

    print(f"🧠 Sending to GPT-5 Mini (detail={detail})...")

    # Simplified System Prompt to reduce errors
    system_prompt = (
        "You are a Savage Roast Master. "
        "Your task is to analyze the user's selfie and generate a 'Drake Hotline Bling' meme.\n"
        "1. Identify the 'vibe' (e.g., tired, messy room, trying too hard).\n"
        "2. Output strictly valid JSON with two keys:\n"
        "   - 'top_text': What they should reject (The 'Nah' face).\n"
        "   - 'bot_text': What they actually do (The 'Yeah' face).\n"
        "3. Keep text under 10 words. Be mean but funny."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini", # <--- FIXED: Use the real model ID
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Roast this image. JSON format only."},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": detail}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
    except Exception as e:
        return {"error": f"API call failed: {str(e)}"}

    # --- DEBUGGING SAFETY REFUSALS ---
    choice = response.choices[0]
    
    # 1. Check if the model refused (Safety Filter)
    if getattr(choice, 'refusal', None):
        print(f"❌ SAFETY REFUSAL: {choice.refusal}")
        return {"error": "AI refused to roast this image (Safety Filter)."}

    # 2. Check if content is empty (Finish Reason)
    content = choice.message.content
    if not content:
        print(f"❌ EMPTY CONTENT. Finish reason: {choice.finish_reason}")
        return {"error": f"AI returned nothing. Reason: {choice.finish_reason}"}

    # 3. Parse JSON
    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError:
        print("❌ JSON PARSE ERROR. Raw output:")
        print(content)
        return {"error": "Invalid JSON"}

# ----------------------------------------------------------------------
# Drake Wrapper
# ----------------------------------------------------------------------
def get_drake_roast(image_path: str) -> Dict[str, str]:
    """
    Returns dictionary with 'top_text' and 'bot_text'
    """
    result = generate_meme_roast(image_path)

    if "error" in result:
        print(f"⚠️  {result['error']}")
        return {"top_text": "AI Failed", "bot_text": "To Roast You"}

    # Return standard keys
    return {
        "top_text": result.get("top_text", "Error"),
        "bot_text": result.get("bot_text", "Error")
    }

# ----------------------------------------------------------------------
# Test Block
# ----------------------------------------------------------------------
if __name__ == "__main__":
    test_path = input("📸 Drag and drop a photo to test: ").strip().replace("'", "").replace('"', "")
    if os.path.exists(test_path):
        roast = get_drake_roast(test_path)
        print("\n✅ RESULT:")
        print(f"Top: {roast['top_text']}")
        print(f"Bot: {roast['bot_text']}")
    else:
        print("File not found.")
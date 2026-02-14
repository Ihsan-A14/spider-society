import os
import sys
from brain import get_roast
from meme_builder import build_meme

def main():
    print("=== 🤖 CS MAJOR ROAST GENERATOR 3000 🤖 ===")
    
    # 1. Get Image
    img_input = input("📸 Drag photo here: ").strip().replace("'", "").replace('"', "")
    if not os.path.exists(img_input):
        print("❌ File not found."); return

    # 2. Get Spice Level
    print("\n🌶️  Select Roast Level:")
    print("   1. Mild (Helpful TA)")
    print("   2. Medium (Sarcastic Senior Dev)")
    print("   3. Savage (Toxic StackOverflow Mod)")
    choice = input("   Choice (1-3): ").strip()
    
    level_map = {"1": "mild", "2": "medium", "3": "savage"}
    roast_level = level_map.get(choice, "medium")

    # 3. Generate
    print(f"\n🧠 Generating {roast_level.upper()} roast...")
    data = get_roast(img_input, roast_level)
    
    if "error" in data:
        print(f"❌ Error: {data['error']}"); return

    print(f"\n✅ Template Selected: {data.get('template')}")
    print(f"📝 Top: {data['top_text']}")
    print(f"📝 Bot: {data['bot_text']}")

    # 4. Build
    outfile = build_meme(data)
    if outfile and sys.platform == "darwin":
        os.system(f"open {outfile}")

if __name__ == "__main__":
    main()
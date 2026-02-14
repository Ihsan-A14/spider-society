import os
import sys
from pathlib import Path

# 1. Setup paths so imports work
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

# 2. Import your modules
# (Make sure your file is actually named 'brain.py'. If it's 'roast_brain.py', change this line!)
from brain import get_drake_roast 
from meme_builder import build_meme

def main():
    print("==========================================")
    print("🔥       DRAKE MEME ROASTER (v1)        🔥")
    print("==========================================")
    
    # 3. Get User Input
    user_input = input("\n📸 Drag & Drop photo here: ").strip()
    # Clean up quotes/spaces from drag-and-drop
    image_path = user_input.replace("'", "").replace('"', "").replace("\\", "")

    if not os.path.exists(image_path):
        print(f"❌ Error: File not found at: {image_path}")
        return

    # 4. Call the Brain
    print("\n🔮 Analyzing vibe & roasting (GPT-4o-Mini)...")
    
    # REMOVED: detail="low" and max_tokens=3000 (The brain handles this internally now)
    roast_data = get_drake_roast(image_path)

    # 5. Handle Errors
    if not roast_data:
        print("❌ Error: Brain returned nothing.")
        return
        
    if "error" in roast_data:
        print(f"\n❌ BRAIN ERROR: {roast_data['error']}")
        if "raw_response" in roast_data:
            print(f"Raw Response: {roast_data['raw_response']}")
        return

    # 6. Success! Show the Text
    print(f"\n🔥 ROAST GENERATED:")
    print(f"   🛑 NAH: {roast_data['top_text']}")
    print(f"   ✅ YEA: {roast_data['bot_text']}")

    # 7. Build the Image
    print("\n🎨 Painting the meme...")
    output_file = build_meme(roast_data)

    if output_file:
        full_path = script_dir / output_file
        print(f"✅ Meme saved as: {full_path}")

        # 8. Auto-Open Logic
        print("🚀 Opening preview...")
        try:
            if sys.platform == "win32":
                os.startfile(str(full_path))
            elif sys.platform == "darwin": # macOS
                os.system(f"open '{full_path}'")
            else:  # Linux
                os.system(f"xdg-open '{full_path}'")
        except Exception as e:
            print(f"(Could not auto-open: {e})")
    else:
        print("❌ Failed to build meme (check meme_builder.py).")

if __name__ == "__main__":
    main()
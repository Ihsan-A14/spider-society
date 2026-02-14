from meme_builder import build_meme
import os
import platform # To check if you are on a Mac

def main():
    print("--- MANUAL MEME GENERATOR (No AI) ---")
    
    # 1. User Input
    top_text = input("Enter TOP text: ").strip()
    bottom_text = input("Enter BOTTOM text: ").strip()
    
    manual_roast_data = {
        "top_text": top_text,
        "bot_text": bottom_text
    }

    # 2. Build the Image
    print("\n🎨 Building your meme...")
    output_filename = build_meme(manual_roast_data)
    
    # 3. AUTO-OPEN LOGIC
    if output_filename and os.path.exists(output_filename):
        print(f"✅ Created {output_filename}")
        
        # Check the operating system
        current_os = platform.system()
        
        if current_os == "Darwin":  # Darwin = macOS
            print("🚀 Opening Preview...")
            os.system(f"open {output_filename}")
        elif current_os == "Windows":
            print("🚀 Opening Windows Photo Viewer...")
            os.startfile(output_filename)
        else:
            print(f"Meme saved. You can find it at: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    main()
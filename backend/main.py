from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

# Import your modules
from brain import get_roast
from meme_builder import build_meme

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("generated_memes", exist_ok=True)

@app.post("/roast")
async def generate_roast_endpoint(
    file: UploadFile = File(...), 
    roast_level: str = Form("medium")
):
    # 1. Setup Paths
    request_id = str(uuid.uuid4())
    temp_input_path = os.path.join("temp_uploads", f"temp_{request_id}.png")
    
    # 2. Save Input File
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"🔥 Processing Request: {request_id}")

    try:
        # 3. Run AI Brain
        roast_data = get_roast(temp_input_path, roast_level=roast_level)
        
        if "error" in roast_data:
            return Response(content=f"Error: {roast_data['error']}", status_code=500)

        # 4. Build Meme
        generated_path = build_meme(roast_data)
        
        if not generated_path or not os.path.exists(generated_path):
            return Response(content="Error: Meme generation failed", status_code=500)

        # ---------------------------------------------------------
        # THE FIX: Read file into RAM, then delete, then send
        # ---------------------------------------------------------
        
        # Read bytes into memory
        with open(generated_path, "rb") as f:
            image_bytes = f.read()
            
        # Delete files from disk NOW (safe because we have the data in 'image_bytes')
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(generated_path):
            os.remove(generated_path)
            
        print(f"✅ Served & Deleted: {generated_path}")

        # Return the bytes directly
        return Response(content=image_bytes, media_type="image/png")

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return Response(content=str(e), status_code=500)

@app.get("/")
def health_check():
    return {"status": "Ready to Roast"}
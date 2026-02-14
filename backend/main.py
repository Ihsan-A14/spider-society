from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

# Import
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

@app.post("/roast")
async def generate_roast_endpoint(
    file: UploadFile = File(...), 
    roast_level: str = Form("medium") # <--- User selects this in frontend
):
    # 1. Save File
    unique_filename = f"temp_{uuid.uuid4()}.png"
    temp_path = os.path.join("temp_uploads", unique_filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Call Brain (Pass the roast level!)
    print(f"🔥 Request: {roast_level} roast")
    roast_data = get_roast(temp_path, roast_level=roast_level)
    
    if "error" in roast_data:
        return {"error": roast_data['error']}

    # 3. Build Meme
    output_filename = build_meme(roast_data)
    
    return FileResponse(output_filename, media_type="image/png")
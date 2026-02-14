from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

# Import your modules
from brain import get_roast
from meme_builder import build_meme

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp folders exist
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("generated_memes", exist_ok=True)

def cleanup_files(file_paths):
    """
    Background task to remove temporary files after the response is sent.
    """
    for path in file_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🧹 Cleaned up: {path}")
            except Exception as e:
                print(f"⚠️ Failed to delete {path}: {e}")

@app.post("/roast")
async def generate_roast_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    roast_level: str = Form("medium")
):
    # 1. Generate Unique ID for this request
    request_id = str(uuid.uuid4())
    input_filename = f"temp_{request_id}.png"
    temp_input_path = os.path.join("temp_uploads", input_filename)
    
    # 2. Save the uploaded file
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"🔥 Request {request_id}: {roast_level} roast")

    # 3. Call Brain
    roast_data = get_roast(temp_input_path, roast_level=roast_level)
    
    if "error" in roast_data:
        # Clean up input immediately if we fail here
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        return {"error": roast_data['error']}

    # 4. Call Builder
    # (Note: You might need to update meme_builder.py to accept a unique output name 
    # if you want to support multiple users at once. For now, we rename it manually.)
    generated_file = build_meme(roast_data)
    
    if not generated_file:
        return {"error": "Builder failed to create image"}

    # Rename the output to avoid overwriting (optional but good practice)
    final_output_path = os.path.join("generated_memes", f"meme_{request_id}.png")
    
    # Move the 'final_meme.png' to our safe folder
    if os.path.exists(generated_file):
        shutil.move(generated_file, final_output_path)
    
    # 5. Schedule Cleanup
    # This runs AFTER the return statement sends the file to the user
    background_tasks.add_task(cleanup_files, [temp_input_path, final_output_path])
    
    # 6. Return the Image
    return FileResponse(final_output_path, media_type="image/png")

@app.get("/")
def health_check():
    return {"status": "Roast API is running", "location": "Edmonton"}
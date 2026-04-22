from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import shutil
from typing import List, Optional
from main import generate_meet_pdf

app = FastAPI(title="Meet Management API", description="API for generating heat sheet PDFs")

def cleanup_temp_dir(dir_path: str):
    """Removes a temporary directory and all its contents."""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

@app.post("/generate")
async def generate_heat_sheet(
    background_tasks: BackgroundTasks,
    meet_name: str = Form(...),
    num_lanes: int = Form(6),
    empty_lanes: bool = Form(False),
    swimmers: List[UploadFile] = File(...),
    relays: Optional[List[UploadFile]] = File(None)
):
    # Create a base temporary directory for this request
    temp_dir = tempfile.mkdtemp(prefix="meet_management_")
    
    # Subdirectories for organized temp files
    data_dir = os.path.join(temp_dir, "data")
    event_out_dir = os.path.join(temp_dir, "event_outputs")
    pdf_out_dir = os.path.join(temp_dir, "pdf_outputs")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(event_out_dir, exist_ok=True)
    os.makedirs(pdf_out_dir, exist_ok=True)
    
    # Schedule cleanup to run after response is sent
    background_tasks.add_task(cleanup_temp_dir, temp_dir)
    
    try:
        swimmer_files = []
        relay_files = []
        
        # Save swimmer files
        for f in swimmers:
            if not f.filename.endswith('.csv'):
                continue
            file_path = os.path.join(data_dir, f.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            swimmer_files.append(file_path)
            
        # Save relay files
        if relays:
            for f in relays:
                if not f.filename.endswith('.csv'):
                    continue
                file_path = os.path.join(data_dir, f.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(f.file, buffer)
                relay_files.append(file_path)
                
        # Call core logic
        pdf_path = generate_meet_pdf(
            meetName=meet_name,
            numLanes=num_lanes,
            emptyLanes=empty_lanes,
            swimmer_files=swimmer_files,
            relay_files=relay_files,
            temp_dir=event_out_dir,
            pdf_out_dir=pdf_out_dir
        )
        
        # Return the generated PDF
        return FileResponse(
            path=pdf_path,
            filename=f"{meet_name}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        # If an error occurs, cleanup still runs via background task? 
        # Actually, if we return an exception, background tasks might not run depending on middleware.
        # But FastAPI does run background tasks on unhandled exceptions in some versions, or we can just let it raise.
        raise HTTPException(status_code=500, detail=str(e))

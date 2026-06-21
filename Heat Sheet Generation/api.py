from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import tempfile
import os
import shutil
from typing import List

from main import generate_meet_pdf
from database import get_db, engine, Base
import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meet Management API", description="API for generating heat sheet PDFs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_temp_dir(dir_path: str):
    """Removes a temporary directory and all its contents."""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

@app.get("/teams")
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return teams

@app.get("/swimmers")
def read_swimmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    swimmers = db.query(models.Swimmer).offset(skip).limit(limit).all()
    return swimmers

@app.get("/meets")
def read_meets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meets = db.query(models.Meet).offset(skip).limit(limit).all()
    return meets

@app.post("/generate")
async def generate_heat_sheet(
    background_tasks: BackgroundTasks,
    meet_id: str = Form(...),
    db: Session = Depends(get_db)
):
    # Fetch meet from database
    meet = db.query(models.Meet).filter(models.Meet.id == meet_id).first()
    if not meet:
        raise HTTPException(status_code=404, detail="Meet not found")
        
    meet_name = meet.name
    num_lanes = meet.num_lanes
    empty_lanes = meet.empty_lanes

    # Create a base temporary directory for this request
    temp_dir = tempfile.mkdtemp(prefix="meet_management_")
    
    # Subdirectories for organized temp files
    event_out_dir = os.path.join(temp_dir, "event_outputs")
    pdf_out_dir = os.path.join(temp_dir, "pdf_outputs")
    
    os.makedirs(event_out_dir, exist_ok=True)
    os.makedirs(pdf_out_dir, exist_ok=True)
    
    # Schedule cleanup to run after response is sent
    background_tasks.add_task(cleanup_temp_dir, temp_dir)
    
    try:
        # Call core logic
        pdf_path = generate_meet_pdf(
            db=db,
            meet_id=meet_id,
            meetName=meet_name,
            numLanes=num_lanes,
            emptyLanes=empty_lanes,
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
        raise HTTPException(status_code=500, detail=str(e))


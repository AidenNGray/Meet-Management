from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import tempfile
import os
import shutil
from typing import List
import pandas as pd
import uuid
import io

from main import generate_meet_pdf
from database import get_db, engine, Base
import models

# Create database tables
Base.metadata.create_all(bind=engine)

# Migrate: add is_active column to swimmers if it doesn't exist
from sqlalchemy import inspect as sa_inspect, text
_insp = sa_inspect(engine)
_cols = [c['name'] for c in _insp.get_columns('swimmers')]
if 'is_active' not in _cols:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE swimmers ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        conn.commit()

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

# --- Phase 3 Endpoints ---

class CoachCreate(BaseModel):
    email: str
    team_id: str

class TeamCreate(BaseModel):
    name: str
    short_id: str

class MeetCreate(BaseModel):
    name: str
    date: str | None = None
    num_lanes: int = 6
    empty_lanes: bool = False
    is_active: bool = False

class EntriesUpdate(BaseModel):
    events: List[str]
    meet_id: str

class SwimmerCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str

class RelayCreate(BaseModel):
    team_id: str
    age_group: str
    gender: str
    stroke: str
    identifier: str
    swimmer1_id: str | None = None
    swimmer2_id: str | None = None
    swimmer3_id: str | None = None
    swimmer4_id: str | None = None

@app.get("/auth/me")
def get_current_user(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # For demo, if they are not in the DB but they logged in, we can either reject or make them a coach with no team.
        # Let's return a 404 so the frontend knows they aren't authorized.
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "role": user.role, "team_id": user.team_id}

@app.get("/active-meet")
def get_active_meet(db: Session = Depends(get_db)):
    meet = db.query(models.Meet).filter(models.Meet.is_active == True).first()
    if not meet:
        raise HTTPException(status_code=404, detail="No active meet found")
    return meet

# --- Meet CRUD ---

@app.post("/admin/meets")
def create_meet(meet: MeetCreate, db: Session = Depends(get_db)):
    from datetime import date as date_type
    meet_date = None
    if meet.date:
        try:
            meet_date = date_type.fromisoformat(meet.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    new_meet = models.Meet(
        id="meet_" + str(uuid.uuid4())[:8],
        name=meet.name,
        date=meet_date,
        num_lanes=meet.num_lanes,
        empty_lanes=meet.empty_lanes,
        is_active=meet.is_active
    )
    db.add(new_meet)
    db.commit()
    return {"message": "Meet created successfully", "id": new_meet.id}

@app.put("/admin/meets/{meet_id}")
def update_meet(meet_id: str, meet: MeetCreate, db: Session = Depends(get_db)):
    from datetime import date as date_type
    existing = db.query(models.Meet).filter(models.Meet.id == meet_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Meet not found")

    existing.name = meet.name
    existing.num_lanes = meet.num_lanes
    existing.empty_lanes = meet.empty_lanes
    existing.is_active = meet.is_active

    if meet.date:
        try:
            existing.date = date_type.fromisoformat(meet.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        existing.date = None

    db.commit()
    return {"message": "Meet updated successfully"}

@app.delete("/admin/meets/{meet_id}")
def delete_meet(meet_id: str, db: Session = Depends(get_db)):
    existing = db.query(models.Meet).filter(models.Meet.id == meet_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Meet not found")

    db.query(models.Entry).filter(models.Entry.meet_id == meet_id).delete()
    db.query(models.RelayEntry).filter(models.RelayEntry.meet_id == meet_id).delete()
    db.delete(existing)
    db.commit()
    return {"message": "Meet deleted successfully"}

@app.get("/meets/{meet_id}/entry-status")
def get_meet_entry_status(meet_id: str, db: Session = Depends(get_db)):
    meet = db.query(models.Meet).filter(models.Meet.id == meet_id).first()
    if not meet:
        raise HTTPException(status_code=404, detail="Meet not found")

    teams = db.query(models.Team).all()
    result = []
    for team in teams:
        total_swimmers = db.query(models.Swimmer).filter(models.Swimmer.team_id == team.id).count()
        if total_swimmers == 0:
            continue
        # Count swimmers that have at least one entry for this meet
        entered_swimmers = (
            db.query(models.Entry.swimmer_id)
            .join(models.Swimmer, models.Entry.swimmer_id == models.Swimmer.id)
            .filter(models.Entry.meet_id == meet_id, models.Swimmer.team_id == team.id)
            .distinct()
            .count()
        )
        result.append({
            "team_id": team.id,
            "team_name": team.name,
            "total_swimmers": total_swimmers,
            "entered_swimmers": entered_swimmers
        })
    return result

@app.post("/admin/coaches")
def create_coach(coach: CoachCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(models.User).filter(models.User.email == coach.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Check if team exists
    team = db.query(models.Team).filter(models.Team.id == coach.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    new_user = models.User(
        id="user_" + str(uuid.uuid4())[:8],
        email=coach.email,
        role="coach",
        team_id=coach.team_id
    )
    db.add(new_user)
    db.commit()
    return {"message": "Coach created successfully"}

@app.post("/admin/teams")
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    # Check if team exists
    existing = db.query(models.Team).filter((models.Team.id == "team_" + team.short_id) | (models.Team.short_id == team.short_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Team with this short ID already exists")

    new_team = models.Team(
        id="team_" + team.short_id,
        name=team.name,
        short_id=team.short_id
    )
    db.add(new_team)
    db.commit()
    return {"message": "Team created successfully", "id": new_team.id}

@app.put("/admin/teams/{team_id}")
def update_team(team_id: str, team: TeamCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if the new short_id conflicts with another team
    if team.short_id != existing.short_id:
        conflict = db.query(models.Team).filter(models.Team.short_id == team.short_id).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Another team already uses this short ID")
            
    existing.name = team.name
    existing.short_id = team.short_id
    db.commit()
    return {"message": "Team updated successfully"}

@app.delete("/admin/teams/{team_id}")
def delete_team(team_id: str, db: Session = Depends(get_db)):
    existing = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
        
    # Also delete associated swimmers, users, and relays or just let cascade handle it? 
    # SQLAlchemy might not cascade automatically if not configured, let's explicitly delete users and swimmers for the team.
    db.query(models.User).filter(models.User.team_id == team_id).delete()
    db.query(models.Swimmer).filter(models.Swimmer.team_id == team_id).delete()
    db.query(models.RelayEntry).filter(models.RelayEntry.team_id == team_id).delete()
    db.delete(existing)
    db.commit()
    return {"message": "Team deleted successfully"}

@app.post("/teams/{team_id}/upload-roster")
async def upload_roster(team_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
        # Expected columns: FirstName, LastName, Gender, Age
        required_cols = ['FirstName', 'LastName', 'Gender', 'Age']
        for col in required_cols:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")
        
        # Add swimmers
        added_count = 0
        for index, row in df.iterrows():
            first_name = str(row['FirstName']).strip()
            last_name = str(row['LastName']).strip()
            gender = str(row['Gender']).strip()
            age = int(row['Age']) if pd.notna(row['Age']) else 0

            # Optional: check if swimmer already exists to avoid duplicates
            existing = db.query(models.Swimmer).filter(
                models.Swimmer.first_name == first_name,
                models.Swimmer.last_name == last_name,
                models.Swimmer.team_id == team_id
            ).first()

            if not existing:
                swimmer = models.Swimmer(
                    id="swim_" + str(uuid.uuid4())[:8],
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    age=age,
                    team_id=team_id
                )
                db.add(swimmer)
                added_count += 1
        
        db.commit()
        return {"message": f"Successfully uploaded roster. Added {added_count} new swimmers."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing Excel file: {str(e)}")

@app.get("/teams/{team_id}/swimmers")
def get_team_swimmers(team_id: str, meet_id: str | None = None, db: Session = Depends(get_db)):
    swimmers = db.query(models.Swimmer).filter(models.Swimmer.team_id == team_id).all()
    
    # Determine which meet to load entries from
    target_meet_id = meet_id
    if not target_meet_id:
        active_meet = db.query(models.Meet).filter(models.Meet.is_active == True).first()
        if active_meet:
            target_meet_id = active_meet.id
    
    result = []
    for s in swimmers:
        events = []
        if target_meet_id:
            entries = db.query(models.Entry).filter(
                models.Entry.swimmer_id == s.id,
                models.Entry.meet_id == target_meet_id
            ).all()
            events = [e.event_type for e in entries]
        
        result.append({
            "id": s.id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "age": s.age,
            "gender": s.gender,
            "is_active": s.is_active if s.is_active is not None else True,
            "events": events
        })
    return result

@app.post("/teams/{team_id}/swimmers")
def add_swimmer(team_id: str, swimmer: SwimmerCreate, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    new_swimmer = models.Swimmer(
        id="swim_" + str(uuid.uuid4())[:8],
        first_name=swimmer.first_name,
        last_name=swimmer.last_name,
        age=swimmer.age,
        gender=swimmer.gender,
        team_id=team_id,
        is_active=True
    )
    db.add(new_swimmer)
    db.commit()
    return {"message": "Swimmer added successfully", "id": new_swimmer.id}

@app.patch("/swimmers/{swimmer_id}/status")
def toggle_swimmer_status(swimmer_id: str, db: Session = Depends(get_db)):
    swimmer = db.query(models.Swimmer).filter(models.Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")
    
    current = swimmer.is_active if swimmer.is_active is not None else True
    swimmer.is_active = not current
    db.commit()
    return {"message": f"Swimmer {'activated' if swimmer.is_active else 'deactivated'}", "is_active": swimmer.is_active}

# --- Relay CRUD ---

@app.get("/meets/{meet_id}/relays")
def get_meet_relays(meet_id: str, team_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.RelayEntry).filter(models.RelayEntry.meet_id == meet_id)
    if team_id:
        query = query.filter(models.RelayEntry.team_id == team_id)
    relays = query.all()
    
    result = []
    for r in relays:
        result.append({
            "id": r.id,
            "meet_id": r.meet_id,
            "team_id": r.team_id,
            "age_group": r.age_group,
            "gender": r.gender,
            "stroke": r.stroke,
            "identifier": r.identifier,
            "swimmer1_id": r.swimmer1_id,
            "swimmer2_id": r.swimmer2_id,
            "swimmer3_id": r.swimmer3_id,
            "swimmer4_id": r.swimmer4_id,
            "swimmer1_name": f"{r.swimmer1.first_name} {r.swimmer1.last_name}" if r.swimmer1 else None,
            "swimmer2_name": f"{r.swimmer2.first_name} {r.swimmer2.last_name}" if r.swimmer2 else None,
            "swimmer3_name": f"{r.swimmer3.first_name} {r.swimmer3.last_name}" if r.swimmer3 else None,
            "swimmer4_name": f"{r.swimmer4.first_name} {r.swimmer4.last_name}" if r.swimmer4 else None,
        })
    return result

@app.post("/meets/{meet_id}/relays")
def create_or_update_relay(meet_id: str, relay: RelayCreate, db: Session = Depends(get_db)):
    # Check meet exists
    meet = db.query(models.Meet).filter(models.Meet.id == meet_id).first()
    if not meet:
        raise HTTPException(status_code=404, detail="Meet not found")
    
    # Check if a relay already exists for this combo
    existing = db.query(models.RelayEntry).filter(
        models.RelayEntry.meet_id == meet_id,
        models.RelayEntry.team_id == relay.team_id,
        models.RelayEntry.age_group == relay.age_group,
        models.RelayEntry.gender == relay.gender,
        models.RelayEntry.stroke == relay.stroke,
        models.RelayEntry.identifier == relay.identifier
    ).first()
    
    if existing:
        # Update
        existing.swimmer1_id = relay.swimmer1_id
        existing.swimmer2_id = relay.swimmer2_id
        existing.swimmer3_id = relay.swimmer3_id
        existing.swimmer4_id = relay.swimmer4_id
        db.commit()
        return {"message": "Relay updated successfully", "id": existing.id}
    else:
        # Create
        new_relay = models.RelayEntry(
            meet_id=meet_id,
            team_id=relay.team_id,
            age_group=relay.age_group,
            gender=relay.gender,
            stroke=relay.stroke,
            identifier=relay.identifier,
            swimmer1_id=relay.swimmer1_id,
            swimmer2_id=relay.swimmer2_id,
            swimmer3_id=relay.swimmer3_id,
            swimmer4_id=relay.swimmer4_id
        )
        db.add(new_relay)
        db.commit()
        return {"message": "Relay created successfully", "id": new_relay.id}

@app.delete("/relays/{relay_id}")
def delete_relay(relay_id: int, db: Session = Depends(get_db)):
    existing = db.query(models.RelayEntry).filter(models.RelayEntry.id == relay_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Relay not found")
    db.delete(existing)
    db.commit()
    return {"message": "Relay deleted successfully"}

@app.post("/swimmers/{swimmer_id}/entries")
def update_swimmer_entries(swimmer_id: str, data: EntriesUpdate, db: Session = Depends(get_db)):
    # Use the meet_id from the request body
    meet = db.query(models.Meet).filter(models.Meet.id == data.meet_id).first()
    if not meet:
        raise HTTPException(status_code=404, detail="Meet not found")
    
    swimmer = db.query(models.Swimmer).filter(models.Swimmer.id == swimmer_id).first()
    if not swimmer:
        raise HTTPException(status_code=404, detail="Swimmer not found")

    # Remove existing entries for this meet
    db.query(models.Entry).filter(
        models.Entry.swimmer_id == swimmer_id,
        models.Entry.meet_id == data.meet_id
    ).delete()

    # Add new entries
    for event_type in data.events:
        entry = models.Entry(
            meet_id=data.meet_id,
            swimmer_id=swimmer_id,
            event_type=event_type
        )
        db.add(entry)
        
    db.commit()
    return {"message": "Entries updated"}

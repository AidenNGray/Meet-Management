import csv
import random
import string
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models
import os

def generate_id(length=5):
    return "".join(random.choices(string.ascii_letters, k=length))

def seed_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    try:
        # Create a meet
        meet_id = "meet_" + generate_id(8)
        print(f"Creating Meet with ID: {meet_id}")
        meet = models.Meet(id=meet_id, name="Test Database Meet", num_lanes=6, empty_lanes=False)
        db.add(meet)
        
        # Create some teams (we'll look at what's in the CSV, e.g. 'hab', 'islands', etc.)
        teams_data = [
            {"id": "team_hab", "name": "Habersham", "short_id": "hab"},
            {"id": "team_islands", "name": "Islands", "short_id": "isl"}
        ]
        
        for t_data in teams_data:
            team = db.query(models.Team).filter(models.Team.short_id == t_data["short_id"]).first()
            if not team:
                team = models.Team(**t_data)
                db.add(team)
                
        db.commit()
        
        # Find swimmer CSVs
        swimmer_files = []
        relay_files = []
        for filename in os.listdir('./Data Files'):
            filepath = os.path.join('./Data Files', filename)
            if "template" in filename.lower():
                continue
            if "relay" in filename.lower() and filename.endswith(".csv"):
                relay_files.append(filepath)
            elif filename.endswith(".csv"):
                swimmer_files.append(filepath)
                
        # Parse swimmer CSVs
        print("Importing Swimmers...")
        for filepath in swimmer_files:
            with open(filepath, 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader) # skips header
                for row in csvReader:
                    if not row or not row[0]: continue
                    
                    # Assume format: First Name,Last Name,Age,Gender,Team,Event 1,Event 2,Event 3,Medley,Free
                    # Wait, swimmer.py CSV format: "first name,last name,gender,age,team,event 1,event 2,event 3,medley relay,free relay"
                    # But the 'June 29 Habersham swim.csv' has First Name,Last Name,Age,Gender,Team...
                    # Let's handle both dynamically or assume the actual CSV column order from June 29:
                    first_name = row[0].strip()
                    last_name = row[1].strip()
                    
                    # Depending on age/gender position:
                    if row[2].isdigit():
                        age = int(row[2])
                        gender = row[3].strip()
                    else:
                        gender = row[2].strip()
                        age = int(row[3])
                        
                    team_short = row[4].strip().lower()
                    e1 = row[5].strip().lower() if len(row) > 5 else ""
                    e2 = row[6].strip().lower() if len(row) > 6 else ""
                    e3 = row[7].strip().lower() if len(row) > 7 else ""
                    
                    team = db.query(models.Team).filter(models.Team.short_id == team_short).first()
                    team_id = team.id if team else "team_hab" # Default to hab if not found
                    
                    swimmer_id = "swim_" + generate_id(8)
                    swimmer = models.Swimmer(
                        id=swimmer_id,
                        first_name=first_name,
                        last_name=last_name,
                        age=age,
                        gender=gender,
                        team_id=team_id
                    )
                    db.add(swimmer)
                    
                    # Add entries
                    for e in [e1, e2, e3]:
                        if e:
                            entry = models.Entry(
                                meet_id=meet_id,
                                swimmer_id=swimmer_id,
                                event_type=e
                            )
                            db.add(entry)
        
        db.commit()
        
        # Parse Relay CSVs
        print("Importing Relays...")
        for filepath in relay_files:
            with open(filepath, 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader) # Skip header
                for row in csvReader:
                    if not row or not row[0]: continue
                    # Format: Team,Age Group,Gender,Stroke,Relay Identifier,Swimmer 1,Swimmer 2,Swimmer 3,Swimmer 4
                    team_name = row[0].strip()
                    age_group = row[1].strip()
                    gender = row[2].strip()
                    stroke = row[3].strip()
                    identifier = row[4].strip()
                    
                    team = db.query(models.Team).filter(models.Team.name.ilike(team_name)).first()
                    team_id = team.id if team else "team_hab"
                    
                    relay = models.RelayEntry(
                        meet_id=meet_id,
                        team_id=team_id,
                        age_group=age_group,
                        gender=gender,
                        stroke=stroke,
                        identifier=identifier
                    )
                    db.add(relay)
                    
        db.commit()
        print("Database seeded successfully.")
        print(f"Use meet_id: '{meet_id}' for /generate endpoint.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

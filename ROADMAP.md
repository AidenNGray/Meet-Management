Meet Management Software: Architecture & Roadmap
1. Project Overview
The goal of this project is to develop a scalable, cloud-native meet management platform comparable to HyTek or SwimTopia. It facilitates swimmer entries, event sorting, and heat sheet generation (PDF) for a summer swim league.

2. Current State (Local Execution)
The system currently operates as a local Python pipeline (located in Heat Sheet Generation/).

Data Ingestion: Reads local CSV files where each row represents a swimmer and their event entries.

Data Models: * Swimmer object: Represents individual athletes.

Event object: Represents a specific race.

Meet object: Aggregates Swimmers and Events, handling the sorting logic.

Output: Generates individual text files for each event, which are then compiled into a single PDF heat sheet (pdfGen.py).

3. Target Architecture (Cloud-Native)
To support multi-user access (coaches, parents, admins) and eliminate local execution requirements, the system is migrating to a serverless Google Cloud / Firebase stack:

Backend Compute: Google Cloud Run (containerized Python API using FastAPI/Flask).

Database: Firebase Firestore (NoSQL) for zero-cost scalability and real-time updates (or Cloud SQL for relational mapping).

Frontend & Hosting: Firebase Hosting (Web dashboard for coaches/parents).

Authentication: Firebase Auth (Role-based access for Admins vs. Guests).

File Storage: Google Cloud Storage (GCS) for storing uploaded CSVs and serving generated PDFs.

4. Development Roadmap
Phase 1: API Transformation (Current Focus)
[ ] Refactor the execution loop in main.py to be callable as a function rather than a standalone script.

[ ] Set up a basic FastAPI application.

[ ] Create an endpoint that accepts a CSV upload, runs the Meet sorting logic, triggers pdfGen.py, and returns the PDF file to the client.

[ ] Containerize the Python application using Docker.

Phase 2: Database Integration
[ ] Design the NoSQL document structure (or SQL schema) for Teams, Swimmers, Meets, and Entries.

[ ] Replace the CSV-parsing logic with database read/write queries.

[ ] Update the Meet object to populate its Swimmers and Events directly from the database.

Phase 3: Frontend Web Portal
[ ] Initialize a web frontend (React, Vue, or Python-based like Reflex/Streamlit) hosted on Firebase.

[ ] Implement secure login for coaches.

[ ] Build a dashboard UI to manage rosters, view meet events, and trigger the Heat Sheet generation API.

Phase 4: Live Results & Expansion
[ ] Build a scoring interface for admins to enter times during the meet.

[ ] Utilize Firestore's real-time listeners to push live result updates to parent/spectator devices in the bleachers.
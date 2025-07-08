from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import uvicorn
import os
import shutil
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect('parking_records.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS parking_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  frame_nmr INTEGER,
                  car_id INTEGER,
                  car_bbox TEXT,
                  license_plate_bbox TEXT,
                  license_plate_bbox_score REAL,
                  license_number TEXT,
                  license_number_score REAL,
                  violation_status TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

class ParkingRecord(BaseModel):
    frame_nmr: int
    car_id: int
    car_bbox: str
    license_plate_bbox: str
    license_plate_bbox_score: float
    license_number: str
    license_number_score: float
    violation_status: str

@app.post("/records/")
async def create_record(record: ParkingRecord):
    conn = sqlite3.connect('parking_records.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT INTO parking_records 
                    (frame_nmr, car_id, car_bbox, license_plate_bbox, 
                     license_plate_bbox_score, license_number, license_number_score, 
                     violation_status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (record.frame_nmr, record.car_id, record.car_bbox, 
                  record.license_plate_bbox, record.license_plate_bbox_score,
                  record.license_number, record.license_number_score,
                  record.violation_status, datetime.now()))
        conn.commit()
        return {"message": "Record added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/records/")
async def get_records():
    conn = sqlite3.connect('parking_records.db')
    c = conn.cursor()
    
    try:
        c.execute('''SELECT * FROM parking_records ORDER BY timestamp DESC''')
        records = c.fetchall()
        
        # Convert records to list of dictionaries
        result = []
        for record in records:
            result.append({
                "id": record[0],
                "frame_nmr": record[1],
                "car_id": record[2],
                "car_bbox": record[3],
                "license_plate_bbox": record[4],
                "license_plate_bbox_score": record[5],
                "license_number": record[6],
                "license_number_score": record[7],
                "violation_status": record[8],
                "timestamp": record[9]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.post("/upload-video/")
async def upload_video(video: UploadFile = File(...)):
    try:
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{video.filename}"
        file_path = UPLOAD_DIR / filename
        
        # Save the uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        return {
            "message": "Video uploaded successfully",
            "filename": filename,
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        video.file.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
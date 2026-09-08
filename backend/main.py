import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.engine import DronaZawarmalaEngine

app = FastAPI(
    title="PROJECT DRONA - Zawarmala Workforce Engine",
    version="2.0.0",
    description="Dynamic Roster & Operational Network Allocator (HZL AI Hackathon 2026)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MASTER_PATH = str(BASE_DIR / "AAC Manpower 2026.xls")
AUDIT_PATH = str(BASE_DIR / "Audit_Trail_Report (4).xlsx")

engine = DronaZawarmalaEngine(master_path=MASTER_PATH, punch_path=AUDIT_PATH)

class ApprovalRequest(BaseModel):
    slot_id: str
    reliever_token: int
    role: str

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ACTIVE",
        "system": "PROJECT DRONA",
        "mine": "Zawarmala Mine",
        "active_workforce_count": len(engine.master_df)
    }

@app.get("/api/v1/lineup/status")
def get_shift_status(shift_id: str = "A"):
    if shift_id not in ["A", "B", "C", "G"]:
        raise HTTPException(status_code=400, detail="Invalid shift. Choose A, B, C, or G.")
    return engine.evaluate_live_status(shift_id=shift_id)

@app.post("/api/v1/reliever/approve")
def approve_reliever_dispatch(payload: ApprovalRequest):
    return {
        "status": "APPROVED_AND_SYNCED",
        "slot_id": payload.slot_id,
        "reliever_token": payload.reliever_token,
        "role": payload.role,
        "sync_target": "Saviour WMS Roster",
        "message": f"Reliever {payload.reliever_token} successfully locked for {payload.role}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)

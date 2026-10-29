from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from .grade_calculator import calculate_record

app = FastAPI(title="AulaControl API", version="0.1.0", description="API inicial para cálculos académicos. No usar aún con datos reales.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class GradeRequest(BaseModel):
    systematic_grades: list[Optional[float]] = Field(default_factory=list)
    partial1: Optional[float] = Field(default=None, ge=0, le=10)
    partial2: Optional[float] = Field(default=None, ge=0, le=10)

class AttendanceRequest(BaseModel):
    attended: int = Field(ge=0)
    computable: int = Field(ge=0)
    justified_absences: int = Field(default=0, ge=0)
    unjustified_absences: int = Field(default=0, ge=0)

@app.get("/")
def root():
    return {"app":"AulaControl API","version":"0.1.0","status":"prototype","docs":"/docs"}

@app.get("/api/v1/health")
def health():
    return {"status":"ok","storage":"in-memory / frontend local","production_ready":False}

@app.post("/api/v1/grades/calculate")
def calculate_grades(payload: GradeRequest):
    try:
        return calculate_record(payload.systematic_grades, payload.partial1, payload.partial2)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/api/v1/attendance/summary")
def attendance_summary(payload: AttendanceRequest):
    if payload.attended > payload.computable:
        raise HTTPException(status_code=422, detail="Las clases asistidas no pueden superar las computables.")
    if payload.justified_absences + payload.unjustified_absences > payload.computable - payload.attended:
        raise HTTPException(status_code=422, detail="Las ausencias registradas superan las ausencias posibles.")
    percentage = (payload.attended / payload.computable * 100) if payload.computable else None
    return {
        "attendance_percentage": percentage,
        "below_threshold": percentage is not None and percentage < 50,
        "justified_absences": payload.justified_absences,
        "unjustified_absences": payload.unjustified_absences,
        "note_penalty_applied": False,
    }

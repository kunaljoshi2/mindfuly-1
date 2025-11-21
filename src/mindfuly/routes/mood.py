from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from src.shared.database import get_db
from src.shared.models import MoodLog
from user_service_v2.models.user import get_user_repository_v2, UserRepositoryV2

router = APIRouter(prefix="/mood", tags=["Mood"])

class MoodLogCreate(BaseModel):
    username: str
    mood_value: int
    energy_level: int
    notes: Optional[str] = None
    weather: Optional[str] = None

class MoodLogResponse(BaseModel):
    id: int
    user_id: int
    mood_value: int
    energy_level: int
    notes: Optional[str]
    weather: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/log", response_model=MoodLogResponse)
async def create_mood_log(
    mood_data: MoodLogCreate,
    db: Session = Depends(get_db),
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)
):
    user = await user_repo.get_by_name(mood_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    mood_log = MoodLog(
        user_id=user.id,
        mood_value=mood_data.mood_value,
        energy_level=mood_data.energy_level,
        notes=mood_data.notes,
        weather=mood_data.weather
    )
    
    db.add(mood_log)
    db.commit()
    db.refresh(mood_log)
    
    return mood_log

@router.get("/logs/{username}", response_model=List[MoodLogResponse])
async def get_mood_logs(
    username: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)
):
    user = await user_repo.get_by_name(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    mood_logs = db.query(MoodLog).filter(
        MoodLog.user_id == user.id
    ).order_by(MoodLog.created_at.desc()).limit(limit).all()
    
    return mood_logs

@router.get("/stats/{username}")
async def get_mood_stats(
    username: str,
    db: Session = Depends(get_db),
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)
):
    user = await user_repo.get_by_name(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from sqlalchemy import func
    
    stats = db.query(
        func.avg(MoodLog.mood_value).label('avg_mood'),
        func.avg(MoodLog.energy_level).label('avg_energy'),
        func.count(MoodLog.id).label('total_logs')
    ).filter(MoodLog.user_id == user.id).first()
    
    return {
        "average_mood": round(float(stats.avg_mood or 0), 2),
        "average_energy": round(float(stats.avg_energy or 0), 2),
        "total_logs": stats.total_logs or 0
    }

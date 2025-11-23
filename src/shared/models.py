from fastapi import Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, insert, select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.shared.database import get_db

from user_service_v2.models.user import Base, get_user_repository_v2, UserRepositoryV2

class MoodLog(Base):
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_value = Column(Integer, nullable=False)
    energy_level = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    weather = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MoodLogRepositoryV2():
    """
    Controls manipulation of the mood_logs table
    """

    def __init__(self, session):
        self.session = session
    
    async def create_mood_log(self,
                                user_id: int,
                                mood_value: int,
                                energy_level: int,
                                notes: Optional[str] = None,
                                weather: Optional[str] = None) -> MoodLog:

        try:
            self.session.execute(insert(MoodLog), [{
                "user_id": user_id,
                "mood_value": mood_value,
                "energy_level": energy_level,
                "notes": notes,
                "weather": weather
            }])
            self.session.commit()
            return MoodLog(
                user_id=user_id,
                mood_value=mood_value,
                energy_level=energy_level,
                notes=notes,
                weather=weather
            )
        except IntegrityError:
            self.session.rollback()
            return None
    
    async def get_mood_logs(self, user_id: int, limit: int = 10) -> list[MoodLog]:
        result = self.session.execute(
            select(MoodLog).where(MoodLog.user_id == user_id).order_by(MoodLog.created_at.desc()).limit(limit)
        )
        mood_logs = result.scalars().all()

        return mood_logs

    async def get_mood_stats(self, user_id: int) -> dict:
        stats = self.session.query(
            func.avg(MoodLog.mood_value).label('avg_mood'),
            func.avg(MoodLog.energy_level).label('avg_energy'),
            func.count(MoodLog.id).label('total_logs')
        ).filter(MoodLog.user_id == user_id).one()

        return {
            "avg_mood": round(float(stats.avg_mood or 0), 2),
            "avg_energy": round(float(stats.avg_energy or 0), 2),
            "total_logs": stats.total_logs or 0
        }

class SpotifySession(Base):
    __tablename__ = "spotify_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_name = Column(String(255), nullable=True)
    artist_name = Column(String(255), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    session_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_mood_log_repository_v2(db: Session = Depends(get_db)) -> MoodLogRepositoryV2:
    return MoodLogRepositoryV2(db)

class MoodLogCreate(BaseModel):
    username: str
    mood_value: int
    energy_level: int
    notes: Optional[str] = None
    weather: Optional[str] = None

class MoodLogResponse(BaseModel):
    user_id: int
    mood_value: int
    energy_level: int
    notes: Optional[str]
    weather: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_db_model(cls, mood_log: MoodLog) -> "MoodLogResponse":
        return cls(
            user_id=mood_log.user_id,
            mood_value=mood_log.mood_value,
            energy_level=mood_log.energy_level,
            notes=mood_log.notes,
            weather=mood_log.weather,
            created_at=datetime.utcnow()  # or mood_log.created_at if you want the original timestamp
        )
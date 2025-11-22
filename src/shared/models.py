from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime

from user_service_v2.models.user import Base, User

class MoodLog(Base):
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_value = Column(Integer, nullable=False)
    energy_level = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    weather = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SpotifySession(Base):
    __tablename__ = "spotify_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_name = Column(String(255), nullable=True)
    artist_name = Column(String(255), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    session_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)




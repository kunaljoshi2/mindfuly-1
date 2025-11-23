from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional

from src.shared.database import get_db
from src.shared.models import MoodLog, MoodLogCreate, MoodLogResponse, get_mood_log_repository_v2, MoodLogRepositoryV2
from user_service_v2.models.user import get_user_repository_v2, UserRepositoryV2

router = APIRouter(prefix="/mood", tags=["Mood"])

@router.post("/log", status_code=201)
async def create_mood_log(
    mood_data: MoodLogCreate,
    response: Response,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    
    user = await user_repo.get_by_name(mood_data.username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        mood_log = await mood_log_repo.create_mood_log(
            user_id=user.id,
            mood_value=mood_data.mood_value,
            energy_level=mood_data.energy_level,
            notes=mood_data.notes,
            weather=mood_data.weather
        )

        return {"mood_log": MoodLogResponse.from_db_model(mood_log)}
    except (IntegrityError, AttributeError):
        response.status_code = 409
        return {"detail": "Something went wrong"}
    
@router.get("/logs/{username}")
async def get_mood_logs(
    username: str,
    limit: int = 10,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2),
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    mood_logs = await mood_log_repo.get_mood_logs(user.id, limit=limit)
    return {"mood_logs": [MoodLogResponse.from_db_model(log) for log in mood_logs]}

@router.get("/stats/{username}")
async def get_mood_stats(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = await mood_log_repo.get_mood_stats(user.id)
    return {"mood_stats": stats}

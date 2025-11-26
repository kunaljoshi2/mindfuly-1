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
    
# Edit the latest mood log for a user
@router.put("/edit_log", status_code=200)
async def edit_mood_log(
    mood_data: MoodLogCreate,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(mood_data.username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    latest_log = await mood_log_repo.get_latest_mood_log(user.id)
    if not latest_log:
        raise HTTPException(status_code=404, detail="No mood log found to edit")
    
    try:
        updated_log = await mood_log_repo.edit_latest_mood_log(
            user_id=user.id,
            mood_value=mood_data.mood_value,
            energy_level=mood_data.energy_level,
            notes=mood_data.notes
        )

        return {"mood_log": MoodLogResponse.from_db_model(updated_log)}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Could not edit mood log")
    
@router.get("/most_recent_log_date/{username}")
async def get_most_recent_log_date(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2),
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    most_recent_date = await mood_log_repo.get_most_recent_log_date(user.id)
    if not most_recent_date:
        return {"most_recent_log_date": None}
    
    return {"most_recent_log_date": most_recent_date.isoformat()}

# Get the latest mood log for a user
@router.get("/latest_log/{username}")
async def get_latest_mood_log(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2),
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    latest_log = await mood_log_repo.get_latest_mood_log(user.id)
    if not latest_log:
        return {"latest_mood_log": None}
    
    return {"latest_mood_log": MoodLogResponse.from_db_model(latest_log)}
    
@router.get("/logs/{username}")
async def get_mood_logs(
    username: str,
    limit: int = 20,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2),
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    mood_logs = await mood_log_repo.get_mood_logs(user.id, limit=limit)
    return {"mood_logs": [MoodLogResponse.from_db_model(log) for log in mood_logs]}

# Get average mood, energy level, and total logs for a user
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

# Get average mood, energy level, and total logs for all days of the week
@router.get("/weekly_stats/{username}")
async def get_weekly_mood_stats(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # TODO: Implement get_weekly_mood_stats in MoodLogRepositoryV2
    weekly_stats = await mood_log_repo.get_weekly_mood_stats(user.id)
    return {"weekly_mood_stats": weekly_stats}

# Get average mood, energy level, and total logs for each weather condition
@router.get("/weather_stats/{username}")
async def get_weather_mood_stats(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    weather_stats = await mood_log_repo.get_weather_mood_stats(user.id)
    return {"weather_mood_stats": weather_stats}

# Get running means for mood and energy levels for every day
@router.get("/running_means/{username}")
async def get_running_means(
    username: str,
    limit: int = 20,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    running_means = await mood_log_repo.get_running_means(user.id, limit=limit)
    return {"running_means": running_means}

# Clear all mood logs for a user
@router.delete("/clear_logs/{username}", status_code=204)
async def clear_mood_logs(
    username: str,
    user_repo: UserRepositoryV2 = Depends(get_user_repository_v2),
    mood_log_repo: MoodLogRepositoryV2 = Depends(get_mood_log_repository_v2)
):
    user = await user_repo.get_by_name(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await mood_log_repo.clear_mood_logs(user.id)
    return Response(status_code=204)
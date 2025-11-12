from typing import List, Optional
from fastapi import FastAPI, Depends, Response, Request, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from shared.database import get_db
import logging
import os
import json
from pathlib import Path
from datetime import datetime, timezone
import asyncio

import user_service_v2.api

# File storage for avatars
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import EmailStr

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

@app.post("/users/", response_model=user_service_v2.api.User, status_code=201)
async def create_user(
    user: user_service_v2.api.UserSchema,
    db: Session = Depends(get_db)
):
    try:
        db_user = user_service_v2.api.create_user(db=db, user=user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="User with this email already exists.")
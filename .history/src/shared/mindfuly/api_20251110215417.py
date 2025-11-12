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
    user: user_service_v2.api.UserCreate
):
    """
    Create a new user.
    """
    try:
        new_user = await user_service_v2.api.create_user(user)
        return new_user
    except IntegrityError as e:
        logger.error(f"Integrity error while creating user: {e}")
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    except Exception as e:
        logger.error(f"Unexpected error while creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

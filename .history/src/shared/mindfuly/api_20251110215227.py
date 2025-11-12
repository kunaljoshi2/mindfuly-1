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

@app.post("/")
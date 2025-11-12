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

# auth module (the init_app pattern)
from . import auth as auth_module
from user_service_v2.models.friendship import FriendshipRepository, get_friendship_repository
from pydantic import EmailStr

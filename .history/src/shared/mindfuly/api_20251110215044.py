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

from user_service_v2.api impo
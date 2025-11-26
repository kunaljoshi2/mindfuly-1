"""
YouTube API integration for mood-based music playback
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
import random

router = APIRouter(prefix="/youtube", tags=["youtube"])

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class VideoInfo(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str


class SearchResults(BaseModel):
    videos: List[VideoInfo]


# Mood-based search queries - multiple options for variety
MOOD_QUERIES = {
    "sad": [
        "sad emotional piano music",
        "melancholic songs playlist",
        "heartbreak songs",
        "emotional music mix",
        "sad indie music playlist"
    ],
    "calm": [
        "calm relaxing music",
        "peaceful ambient music",
        "chill acoustic music",
        "soft background music",
        "calm piano music"
    ],
    "peaceful": [
        "peaceful meditation music",
        "zen relaxation music",
        "nature sounds music",
        "tranquil spa music",
        "peaceful guitar music"
    ],
    "happy": [
        "happy upbeat music",
        "feel good songs",
        "positive vibes playlist",
        "cheerful pop music",
        "happy indie music"
    ],
    "energetic": [
        "energetic workout music",
        "upbeat gym music",
        "high energy dance music",
        "motivational workout songs",
        "powerful electronic music"
    ],
    "focused": [
        "focus study music lofi",
        "deep focus music",
        "concentration music",
        "productivity music",
        "study beats"
    ],
    "chill": [
        "chill lofi hip hop",
        "relaxing beats",
        "chillout music mix",
        "lazy day playlist",
        "downtempo music"
    ],
    "motivated": [
        "motivational music",
        "epic inspirational music",
        "powerful workout motivation",
        "success music",
        "pump up songs"
    ]
}


@router.get("/search/by-mood/{mood}", response_model=SearchResults)
async def search_by_mood(mood: str, max_results: int = 10):
    """
    Search for music videos based on mood - randomly selects from multiple query options
    """
    if not YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="YouTube API key not configured"
        )
    
    # Get the search queries for this mood
    mood_queries = MOOD_QUERIES.get(mood.lower())
    
    if mood_queries:
        # Randomly select one of the query options for variety
        query = random.choice(mood_queries)
    else:
        # Fallback for unknown moods
        query = f"{mood} music playlist"
    
    try:
        async with httpx.AsyncClient() as client:
            # Request more results to give us room to shuffle
            response = await client.get(
                YOUTUBE_SEARCH_URL,
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "videoCategoryId": "10",  # Music category
                    "maxResults": min(max_results * 2, 50),  # Get 2x results for better variety
                    "key": YOUTUBE_API_KEY,
                    "safeSearch": "moderate"
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"YouTube API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            
            data = response.json()
            
            videos = []
            for item in data.get("items", []):
                videos.append(VideoInfo(
                    video_id=item["id"]["videoId"],
                    title=item["snippet"]["title"],
                    channel=item["snippet"]["channelTitle"],
                    thumbnail=item["snippet"]["thumbnails"]["medium"]["url"]
                ))
            
            # Shuffle the videos for random playback order
            random.shuffle(videos)
            
            # Return only the requested number of videos
            return SearchResults(videos=videos[:max_results])
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to YouTube API: {str(e)}"
        )


@router.get("/search", response_model=SearchResults)
async def search_videos(query: str, max_results: int = 10):
    """
    Search for music videos by query - results are randomized
    """
    if not YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="YouTube API key not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                YOUTUBE_SEARCH_URL,
                params={
                    "part": "snippet",
                    "q": f"{query} music",
                    "type": "video",
                    "videoCategoryId": "10",  # Music category
                    "maxResults": min(max_results * 2, 50),  # Get more for variety
                    "key": YOUTUBE_API_KEY,
                    "safeSearch": "moderate"
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"YouTube API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            
            data = response.json()
            
            videos = []
            for item in data.get("items", []):
                videos.append(VideoInfo(
                    video_id=item["id"]["videoId"],
                    title=item["snippet"]["title"],
                    channel=item["snippet"]["channelTitle"],
                    thumbnail=item["snippet"]["thumbnails"]["medium"]["url"]
                ))
            
            # Shuffle for random playback
            random.shuffle(videos)
            
            return SearchResults(videos=videos[:max_results])
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to YouTube API: {str(e)}"
        )


@router.get("/moods")
async def get_available_moods():
    """
    Get list of available moods
    """
    return {
        "moods": list(MOOD_QUERIES.keys())
    }


"""
Playlist storage module for my_reader TTS
Manages persistent playlist data using HuggingFace Spaces storage
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# HuggingFace Spaces persistent storage path
STORAGE_PATH = Path("/storage/playlist")


def ensure_storage_dir():
    """Ensure storage directory exists"""
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)


def get_playlist_file() -> Path:
    """Get path to playlist metadata file"""
    ensure_storage_dir()
    return STORAGE_PATH / "playlist.json"


def load_playlist() -> List[Dict[str, Any]]:
    """Load playlist from storage"""
    playlist_file = get_playlist_file()
    
    if not playlist_file.exists():
        return []
    
    try:
        with open(playlist_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_playlist(playlist: List[Dict[str, Any]]):
    """Save playlist to storage"""
    playlist_file = get_playlist_file()
    ensure_storage_dir()
    
    with open(playlist_file, 'w') as f:
        json.dump(playlist, f, indent=2)


def get_audio_file(item_id: str) -> Path:
    """Get path to audio file for a playlist item"""
    ensure_storage_dir()
    return STORAGE_PATH / f"{item_id}.wav"


def add_to_playlist(
    text: str,
    audio_data: bytes,
    voice: str,
    speed: float,
    source: str = "text",
    url: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a new item to the playlist
    
    Args:
        text: The text that was converted to audio
        audio_data: WAV audio bytes
        voice: Voice ID used
        speed: Speed multiplier
        source: "text" or "url"
        url: Original URL if source is "url"
        title: Optional title (for URLs)
    
    Returns:
        The created playlist item
    """
    # Generate unique ID
    item_id = str(uuid.uuid4())
    
    # Calculate duration (approximate: 24000 samples/sec, 16-bit mono)
    # WAV header is 44 bytes, then 2 bytes per sample
    audio_size = len(audio_data)
    duration_samples = (audio_size - 44) / 2
    duration_seconds = duration_samples / 24000
    
    # Create playlist item
    item = {
        "id": item_id,
        "text": text[:500],  # Store first 500 chars for preview
        "full_text": text,  # Store full text for regeneration if needed
        "voice": voice,
        "speed": speed,
        "source": source,
        "url": url,
        "title": title or text[:100],
        "duration": round(duration_seconds, 1),
        "created_at": datetime.now().isoformat(),
        "file_size": audio_size
    }
    
    # Save audio file
    audio_file = get_audio_file(item_id)
    with open(audio_file, 'wb') as f:
        f.write(audio_data)
    
    # Add to playlist
    playlist = load_playlist()
    playlist.append(item)
    save_playlist(playlist)
    
    return item


def get_playlist_item(item_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific playlist item"""
    playlist = load_playlist()
    for item in playlist:
        if item["id"] == item_id:
            return item
    return None


def get_audio_bytes(item_id: str) -> Optional[bytes]:
    """Get audio bytes for a playlist item"""
    audio_file = get_audio_file(item_id)
    
    if not audio_file.exists():
        return None
    
    with open(audio_file, 'rb') as f:
        return f.read()


def delete_from_playlist(item_id: str) -> bool:
    """
    Delete an item from the playlist
    
    Returns:
        True if deleted, False if not found
    """
    playlist = load_playlist()
    
    # Find and remove item
    original_length = len(playlist)
    playlist = [item for item in playlist if item["id"] != item_id]
    
    if len(playlist) == original_length:
        return False
    
    # Delete audio file
    audio_file = get_audio_file(item_id)
    if audio_file.exists():
        audio_file.unlink()
    
    # Save updated playlist
    save_playlist(playlist)
    
    return True


def reorder_playlist(item_id: str, new_index: int) -> bool:
    """
    Move a playlist item to a new position
    
    Args:
        item_id: ID of item to move
        new_index: New position (0-based)
    
    Returns:
        True if successful, False if item not found
    """
    playlist = load_playlist()
    
    # Find item
    current_index = None
    for i, item in enumerate(playlist):
        if item["id"] == item_id:
            current_index = i
            break
    
    if current_index is None:
        return False
    
    # Remove and re-insert
    item = playlist.pop(current_index)
    
    # Clamp index to valid range
    new_index = max(0, min(new_index, len(playlist)))
    playlist.insert(new_index, item)
    
    save_playlist(playlist)
    return True


def clear_playlist() -> int:
    """
    Delete all items from the playlist
    
    Returns:
        Number of items deleted
    """
    playlist = load_playlist()
    count = len(playlist)
    
    # Delete all audio files
    for item in playlist:
        audio_file = get_audio_file(item["id"])
        if audio_file.exists():
            audio_file.unlink()
    
    # Clear playlist
    save_playlist([])
    
    return count


def get_playlist_stats() -> Dict[str, Any]:
    """Get playlist statistics"""
    playlist = load_playlist()
    
    total_size = sum(item.get("file_size", 0) for item in playlist)
    total_duration = sum(item.get("duration", 0) for item in playlist)
    
    return {
        "item_count": len(playlist),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "total_duration_seconds": round(total_duration, 1),
        "total_duration_formatted": format_duration(total_duration)
    }


def format_duration(seconds: float) -> str:
    """Format duration as MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

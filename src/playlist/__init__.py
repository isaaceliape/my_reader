"""Playlist module for my_reader TTS"""

from .storage import (
    add_to_playlist,
    get_playlist_item,
    get_audio_bytes,
    delete_from_playlist,
    reorder_playlist,
    clear_playlist,
    load_playlist,
    get_playlist_stats,
)

__all__ = [
    "add_to_playlist",
    "get_playlist_item",
    "get_audio_bytes",
    "delete_from_playlist",
    "reorder_playlist",
    "clear_playlist",
    "load_playlist",
    "get_playlist_stats",
]

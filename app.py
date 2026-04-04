"""
Local TTS Web App - Kokoro TTS Backend
Optimized for CPU and GPU inference
"""

import io
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from kokoro import KPipeline
from src.crawler.integrator import process_url_to_audio
from src.crawler.cache import cache_invalidate, cache_clear
from src.playlist import (
    add_to_playlist,
    get_playlist_item,
    get_audio_bytes,
    delete_from_playlist,
    reorder_playlist,
    clear_playlist,
    load_playlist,
    get_playlist_stats,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optimize PyTorch for CPU inference
# Set before any CUDA/MPS checks to ensure CPU optimization
def optimize_cpu_settings():
    """Optimize PyTorch for CPU inference"""
    # Set number of threads for CPU
    torch.set_num_threads(4)  # Optimal for most CPU workloads
    
    # Enable MKL-DNN optimizations (Intel CPUs)
    if hasattr(torch.backends, 'mkldnn'):
        torch.backends.mkldnn.enabled = True
    
    # Set float32 matrix multiplication precision
    torch.set_float32_matmul_precision('medium')  # 'high' for accuracy, 'medium' for speed
    
    # Disable gradients for inference (saves memory)
    torch.set_grad_enabled(False)
    
    logger.info("CPU optimization settings applied")

# Apply CPU optimizations at module load
optimize_cpu_settings()


# Global TTS pipeline (loaded lazily on first request)
pipeline = None
pipeline_loading = False


def get_or_load_pipeline():
    """Get pipeline, loading it if necessary (lazy loading)"""
    global pipeline, pipeline_loading
    
    if pipeline is not None:
        return pipeline
    
    if pipeline_loading:
        # Already loading, wait a bit and try again
        import time
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if pipeline is not None:
                return pipeline
        raise HTTPException(status_code=503, detail="Model still loading, please try again")
    
    # Start loading
    pipeline_loading = True
    logger.info("Loading Kokoro pipeline on first request...")
    
    if load_kokoro_pipeline():
        logger.info("Kokoro pipeline loaded successfully!")
        return pipeline
    else:
        pipeline_loading = False
        raise HTTPException(status_code=500, detail="Failed to load TTS model")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager - no startup loading, lazy load instead"""
    logger.info("App starting (model will load on first request)...")
    yield
    logger.info("App shutting down...")


# Initialize FastAPI app with lifespan (no startup loading)
app = FastAPI(
    title="Local TTS Web App",
    description="Text-to-Speech powered by Kokoro TTS - runs locally on M1",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend) - serve at /static path
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount(
        "/static", StaticFiles(directory=str(static_path), html=True), name="static"
    )
    logger.info(f"Serving static files from {static_path}")


def get_device():
    """Detect best available device with CPU optimizations"""
    # Check for CUDA (NVIDIA GPU) - primary for HuggingFace Spaces
    if torch.cuda.is_available():
        device = "cuda"
        cuda_device = torch.cuda.current_device()
        cuda_name = torch.cuda.get_device_name(cuda_device)
        cuda_memory = torch.cuda.get_device_properties(cuda_device).total_memory / (1024**3)
        logger.info(f"Using CUDA GPU: {cuda_name} ({cuda_memory:.1f}GB VRAM)")
        logger.info(f"CUDA Version: {torch.version.cuda}")
        return device
    
    # Check for MPS (Apple Silicon) - for local development on M1/M2
    if torch.backends.mps.is_available():
        logger.info("Using MPS (Metal Performance Shaders) for GPU acceleration")
        logger.info("Note: MPS is optimized for Apple Silicon")
        return "mps"
    
    # CPU with optimizations
    logger.info("Using CPU with optimizations")
    logger.info(f"PyTorch threads: {torch.get_num_threads()}")
    logger.info(f"MKL-DNN enabled: {torch.backends.mkldnn.enabled if hasattr(torch.backends, 'mkldnn') else 'N/A'}")
    logger.info(f"Matrix precision: {torch.get_float32_matmul_precision()}")
    logger.info("CPU Optimization tips:")
    logger.info("  - Enable GPU in HuggingFace Spaces Settings for 10-50x speedup")
    logger.info("  - T4 Small GPU costs $0.20/hour")
    return "cpu"


def load_kokoro_pipeline():
    """Load Kokoro TTS pipeline - called once at startup"""
    global pipeline

    device = get_device()

    try:
        logger.info("Loading Kokoro TTS pipeline...")
        # Use English language model
        pipeline = KPipeline(lang_code="a", device=device)
        logger.info("Kokoro pipeline loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to load Kokoro pipeline: {e}")
        return False


def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes:
    """Generate audio from text using Kokoro TTS"""
    # Load pipeline if not already loaded (lazy loading)
    current_pipeline = get_or_load_pipeline()
    
    try:
        # Kokoro pipeline is callable - returns a generator of Results
        # Each Result has: audio (torch.Tensor), phonemes, graphemes, etc.
        results = current_pipeline(text, voice=voice, speed=speed)

        # Collect all audio segments (Kokoro may split long text)
        audio_segments = []
        sample_rate = 24000  # Kokoro uses 24kHz

        for result in results:
            audio = result.audio
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()
            audio_segments.append(audio)

        # Concatenate all segments
        if len(audio_segments) == 1:
            audio_samples = audio_segments[0]
        else:
            audio_samples = np.concatenate(audio_segments)

        # Write to WAV format in memory
        buffer = io.BytesIO()
        sf.write(buffer, audio_samples, sample_rate, format="WAV")
        buffer.seek(0)

        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    from fastapi.responses import FileResponse

    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "status": "ok",
        "service": "Local TTS Web App",
        "tts_loaded": pipeline is not None,
    }


@app.get("/api")
async def api_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Local TTS Web App",
        "tts_loaded": pipeline is not None,
    }


@app.get("/voices")
async def list_voices():
    """List available voices"""
    # Kokoro has multiple voices - here are the curated ones
    voices = [
        {"id": "af_heart", "name": "Heart (Female)", "language": "en-US"},
        {"id": "af_sarah", "name": "Sarah (Female)", "language": "en-US"},
        {"id": "am_adam", "name": "Adam (Male)", "language": "en-US"},
        {"id": "am_michael", "name": "Michael (Male)", "language": "en-US"},
        {"id": "bf_emma", "name": "Emma (Female, British)", "language": "en-GB"},
        {
            "id": "bf_isabella",
            "name": "Isabella (Female, British)",
            "language": "en-GB",
        },
    ]
    return {"voices": voices}


@app.post("/tts")
async def text_to_speech(
    text: str = Body(...), 
    voice: str = Body("af_heart"), 
    speed: float = Body(1.0),
    add_to_playlist: bool = Body(True)
):
    """
    Generate speech from text

    Args:
        text: Text to synthesize
        voice: Voice ID to use
        speed: Playback speed (0.5 to 2.0)
        add_to_playlist: Whether to add to playlist (default: True)
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    if len(text) > 5000:
        raise HTTPException(
            status_code=400, detail="Text too long (max 5000 characters)"
        )

    try:
        logger.info(f"Generating TTS: {len(text)} chars, voice={voice}, speed={speed}")

        # Generate audio
        audio_data = generate_audio(text, voice, speed)

        # Add to playlist if requested
        playlist_item_id = None
        if add_to_playlist:
            try:
                item = add_to_playlist(
                    text=text,
                    audio_data=audio_data,
                    voice=voice,
                    speed=speed,
                    source="text"
                )
                playlist_item_id = item["id"]
                logger.info(f"Added to playlist: {playlist_item_id}")
            except Exception as e:
                import traceback
                logger.error(f"Failed to add to playlist: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue anyway - playlist is optional

        # Return as WAV stream
        headers = {
            "Content-Disposition": "attachment; filename=speech.wav",
            "Cache-Control": "no-cache",
        }
        
        if playlist_item_id:
            headers["X-Playlist-Item-ID"] = playlist_item_id

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers=headers,
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/url")
async def url_to_audio(
    url: str = Body(...),
    voice: str = Body("af_heart"),
    speed: float = Body(1.0),
    add_to_playlist: bool = Body(True)
):
    """
    Process a URL to extract article content and generate audio.

    Args:
        url: URL of the article to process
        voice: Voice ID to use (default: "af_heart")
        speed: Playback speed 0.5-2.0 (default: 1.0)
        add_to_playlist: Whether to add to playlist (default: True)

    Returns:
        StreamingResponse with audio and metadata headers
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        logger.info(f"Processing URL: {url}, voice={voice}, speed={speed}")

        # Process URL through crawler
        article, error, cache_hit = process_url_to_audio(url, voice, speed)

        if article is None:
            # Determine appropriate status code based on error
            error_lower = (error or "").lower()
            if "authentication" in error_lower or "blocking" in error_lower:
                raise HTTPException(status_code=403, detail=error)
            elif "timeout" in error_lower:
                raise HTTPException(status_code=504, detail=error)
            else:
                raise HTTPException(status_code=400, detail=error or "Unknown error")

        # Generate audio from extracted text
        if not article.text or len(article.text.strip()) == 0:
            raise HTTPException(
                status_code=400, detail="No text content extracted from URL"
            )

        logger.info(
            f"Generated audio from article: {article.title} ({len(article.text)} chars)"
        )

        # Generate audio
        audio_data = generate_audio(article.text, voice, speed)

        # Add to playlist if requested
        playlist_item_id = None
        if add_to_playlist:
            try:
                item = add_to_playlist(
                    text=article.text,
                    audio_data=audio_data,
                    voice=voice,
                    speed=speed,
                    source="url",
                    url=article.url,
                    title=article.title
                )
                playlist_item_id = item["id"]
                logger.info(f"Added to playlist: {playlist_item_id}")
            except Exception as e:
                import traceback
                logger.error(f"Failed to add to playlist: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue anyway - playlist is optional

        # Prepare response headers with metadata
        headers = {
            "X-Article-Title": article.title,
            "X-Article-URL": article.url,
            "X-Cache": "HIT" if cache_hit else "MISS",
            "Content-Disposition": f'attachment; filename="{article.title}.wav"',
        }

        if article.language:
            headers["X-Article-Language"] = article.language
        
        if playlist_item_id:
            headers["X-Playlist-Item-ID"] = playlist_item_id

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers=headers,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache")
async def invalidate_cache(url: str = Body(...)):
    """
    Invalidate cached content for a specific URL.

    Args:
        url: URL to invalidate from cache

    Returns:
        JSON response with invalidation status
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        logger.info(f"Invalidating cache for URL: {url}")

        invalidated = cache_invalidate(url)

        if invalidated:
            return {"status": "success", "message": "Cache invalidated", "url": url}
        else:
            return {"status": "not_found", "message": "URL not in cache", "url": url}

    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache/all")
async def clear_all_cache():
    """
    Clear all cached content.

    Returns:
        JSON response with confirmation
    """
    try:
        logger.info("Clearing all cache")
        cache_clear()
        return {"status": "success", "message": "All cache cleared"}
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Playlist API Endpoints ==============

@app.get("/api/playlist")
async def get_playlist():
    """Get all playlist items"""
    try:
        playlist = load_playlist()
        stats = get_playlist_stats()
        return {
            "items": playlist,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to load playlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/playlist/{item_id}")
async def get_playlist_item_endpoint(item_id: str):
    """Get a specific playlist item"""
    item = get_playlist_item(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.get("/api/playlist/{item_id}/audio")
async def get_playlist_audio(item_id: str):
    """Get audio file for a playlist item"""
    audio_data = get_audio_bytes(item_id)
    
    if not audio_data:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    item = get_playlist_item(item_id)
    filename = f"{item['title'][:50]}.wav" if item else "audio.wav"
    
    return StreamingResponse(
        io.BytesIO(audio_data),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )


@app.delete("/api/playlist/{item_id}")
async def delete_playlist_item(item_id: str):
    """Delete a playlist item"""
    success = delete_from_playlist(item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"status": "success", "message": "Item deleted"}


@app.put("/api/playlist/{item_id}/reorder")
async def reorder_playlist_item(item_id: str, new_index: int = Body(...)):
    """Reorder a playlist item"""
    success = reorder_playlist(item_id, new_index)
    
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"status": "success", "message": "Item reordered"}


@app.delete("/api/playlist")
async def clear_playlist_endpoint():
    """Clear all playlist items"""
    count = clear_playlist()
    return {
        "status": "success",
        "message": f"Deleted {count} items",
        "deleted_count": count
    }


@app.post("/api/playlist/add-to-queue")
async def add_to_queue(item_id: str = Body(...)):
    """Add playlist item to playback queue"""
    item = get_playlist_item(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {
        "status": "success",
        "item": item
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Local TTS Web App...")
    logger.info("Accessible at: http://0.0.0.0:8000 (all network interfaces)")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

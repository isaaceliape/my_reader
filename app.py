"""
Local TTS Web App - Kokoro TTS Backend
Runs entirely locally on MacBook Air M1
"""

import io
import os
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Local TTS Web App",
    description="Text-to-Speech powered by Kokoro TTS - runs locally on M1",
    version="0.1.0"
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
    app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")
    logger.info(f"Serving static files from {static_path}")

# Global TTS pipeline (loaded once at startup)
pipeline = None


def get_device():
    """Detect best available device for M1 Mac"""
    if torch.backends.mps.is_available():
        logger.info("Using MPS (Metal Performance Shaders) for GPU acceleration")
        return "mps"
    elif torch.cuda.is_available():
        logger.info("Using CUDA GPU")
        return "cuda"
    else:
        logger.info("Using CPU (no GPU available)")
        return "cpu"


def load_kokoro_pipeline():
    """Load Kokoro TTS pipeline - called once at startup"""
    global pipeline
    
    device = get_device()
    
    try:
        logger.info("Loading Kokoro TTS pipeline...")
        # Use English language model
        pipeline = KPipeline(lang_code='a', device=device)
        logger.info("Kokoro pipeline loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to load Kokoro pipeline: {e}")
        return False


def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes:
    """Generate audio from text using Kokoro TTS"""
    global pipeline
    
    if pipeline is None:
        raise RuntimeError("TTS pipeline not loaded")
    
    try:
        # Kokoro pipeline is callable - returns a generator of Results
        # Each Result has: audio (torch.Tensor), phonemes, graphemes, etc.
        results = pipeline(text, voice=voice, speed=speed)
        
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
        sf.write(buffer, audio_samples, sample_rate, format='WAV')
        buffer.seek(0)
        
        return buffer.getvalue()
    
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Load TTS model on startup"""
    load_kokoro_pipeline()


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    from fastapi.responses import FileResponse
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"status": "ok", "service": "Local TTS Web App", "tts_loaded": pipeline is not None}


@app.get("/api")
async def api_root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Local TTS Web App",
        "tts_loaded": pipeline is not None
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
        {"id": "bf_isabella", "name": "Isabella (Female, British)", "language": "en-GB"},
    ]
    return {"voices": voices}


@app.post("/tts")
async def text_to_speech(
    text: str = Body(...),
    voice: str = Body("af_heart"),
    speed: float = Body(1.0)
):
    """
    Generate speech from text
    
    Args:
        text: Text to synthesize
        voice: Voice ID to use
        speed: Playback speed (0.5 to 2.0)
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    try:
        logger.info(f"Generating TTS: {len(text)} chars, voice={voice}, speed={speed}")
        
        # Generate audio
        audio_data = generate_audio(text, voice, speed)
        
        # Return as WAV stream
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "Cache-Control": "no-cache"
            }
        )
    
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Local TTS Web App...")
    logger.info("Accessible at: http://0.0.0.0:8000 (all network interfaces)")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

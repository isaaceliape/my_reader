"""
Vercel Serverless Function Entry Point for my_reader TTS API

This file adapts the FastAPI app for Vercel's serverless Python runtime.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel
os.environ["VERCEL"] = "1"
os.environ["HERMES_HOME"] = "/tmp/.hermes"  # Use tmp for serverless

from fastapi import FastAPI
from mangum import Mangum

# Import the main app
from app import app as fastapi_app

# Create Mangum handler for ASGI -> Vercel adapter
# Vercel expects 'app' or 'handler' at module level
app = Mangum(fastapi_app, lifespan="off")

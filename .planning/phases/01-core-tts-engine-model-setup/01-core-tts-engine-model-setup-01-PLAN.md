---
phase: 01-core-tts-engine-model-setup
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - requirements.txt
  - .gitignore
  - src/__init__.py
  - src/tts/__init__.py
  - src/tts/device.py
  - src/tts/voices.py
  - config/voices.json
autonomous: true

must_haves:
  truths:
    - "Python project structure created with proper package layout"
    - "All dependencies installable via pip"
    - "MPS/CPU device detection works with automatic fallback"
    - "2-3 curated voices configured and loadable"
  artifacts:
    - path: "requirements.txt"
      provides: "Python dependencies (kokoro, torch, soundfile)"
      contains: ["kokoro>=0.9.4", "torch", "soundfile"]
    - path: "src/tts/device.py"
      provides: "MPS/CPU device detection with fallback"
      exports: ["get_optimal_device"]
    - path: "src/tts/voices.py"
      provides: "Voice manager with lazy loading"
      exports: ["VoiceManager", "VOICE_CONFIGS"]
    - path: "config/voices.json"
      provides: "Curated voice configurations"
      contains: ["af_heart", "am_echo"]
  key_links:
    - from: "src/tts/voices.py"
      to: "KPipeline"
      via: "pipeline.load_voice()"
      pattern: "load_voice"
---

<objective>
Set up Python project structure, install dependencies, and implement device detection and voice management modules.

Purpose: This plan establishes the foundation for the TTS engine — project structure, hardware detection for M1 optimization, and voice configuration. Without these basics, no audio generation can happen.
Output: Working device detection (MPS with CPU fallback) and voice manager ready to load 2-3 curated voices.
</objective>

<execution_context>
@/Users/isaaceliape/.config/opencode/get-shit-done/workflows/execute-plan.md
@/Users/isaaceliape/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-core-tts-engine-model-setup/01-RESEARCH.md

## Key Technical Details

**Kokoro Installation:**
```bash
pip install kokoro>=0.9.4
pip install soundfile>=0.13.0
```

**Device Detection Pattern:**
```python
import torch

def get_optimal_device():
    if torch.backends.mps.is_available():
        try:
            test = torch.zeros(1).to('mps')
            return 'mps'
        except:
            return 'cpu'
    return 'cpu'
```

**Recommended Voices (curated 2-3):**
- af_heart: Female, warm natural tone
- am_echo: Male, clear professional
- bf_emma: Female, British accent variety

**Voice Config Structure:**
```json
{
  "af_heart": {"lang": "a", "gender": "female", "quality": "excellent"},
  "am_echo": {"lang": "a", "gender": "male", "quality": "excellent"}
}
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Python Project Structure and Dependencies</name>
  <files>
    requirements.txt
    .gitignore
    src/__init__.py
    src/tts/__init__.py
  </files>
  <action>
Create the Python project structure for the TTS application.

1. Create directory structure:
   - src/tts/ (main TTS package)
   - config/ (voice configurations)
   - tests/ (test files)
   - models/ (downloaded model files, gitignored)

2. Create requirements.txt with:
   ```
   kokoro>=0.9.4
   torch>=2.2.0
   soundfile>=0.13.0
   numpy<2.0.0
   ```
   Note: numpy<2.0.0 avoids compatibility issues with some audio libraries

3. Create .gitignore:
   ```
   __pycache__/
   *.pyc
   .venv/
   venv/
   models/
   *.wav
   *.mp3
   .DS_Store
   ```

4. Create src/__init__.py and src/tts/__init__.py with package docstring

5. Create a basic README.md in src/tts/ explaining the package structure
  </action>
  <verify>
    python -c "import sys; print(sys.version)"  # Verify Python 3.10+
    ls -la src/tts/__init__.py  # Verify structure exists
  </verify>
  <done>
    Project structure created with src/tts/ package, requirements.txt with kokoro>=0.9.4, and .gitignore excluding models/ and audio files
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement Device Detection Module</name>
  <files>src/tts/device.py</files>
  <action>
Create src/tts/device.py with MPS/CPU detection and fallback logic.

Implementation requirements:
```python
"""Device detection for optimal TTS inference."""
import torch
import logging

logger = logging.getLogger(__name__)


def get_optimal_device() -> str:
    """
    Detect optimal device for TTS inference.
    
    Priority: MPS (Apple Silicon) -> CPU
    Falls back to CPU if MPS test fails.
    
    Returns:
        Device string: 'mps' or 'cpu'
    """
    # Check MPS availability
    if torch.backends.mps.is_available():
        try:
            # Test MPS with a small tensor operation
            test_tensor = torch.zeros(1, device='mps')
            _ = test_tensor * 2  # Simple operation to verify
            logger.info("Using MPS (Metal Performance Shaders) device")
            return 'mps'
        except Exception as e:
            logger.warning(f"MPS available but test failed: {e}. Falling back to CPU.")
            return 'cpu'
    
    logger.info("Using CPU device")
    return 'cpu'


def get_device_info() -> dict:
    """Get detailed device information for debugging."""
    return {
        'device': get_optimal_device(),
        'mps_available': torch.backends.mps.is_available(),
        'mps_built': torch.backends.mps.is_built() if hasattr(torch.backends.mps, 'is_built') else 'unknown',
        'torch_version': torch.__version__,
    }
```

Key points:
- Must test MPS with actual tensor operation (not just is_available())
- Log device selection for debugging
- Provide get_device_info() for troubleshooting
  </action>
  <verify>
    cd /Users/isaaceliape/repos/my_reader && python -c "from src.tts.device import get_optimal_device, get_device_info; print(get_device_info())"
  </verify>
  <done>
    Device detection returns 'mps' or 'cpu', get_device_info() provides diagnostic details including torch version and MPS availability
  </done>
</task>

<task type="auto">
  <name>Task 3: Implement Voice Manager with Lazy Loading</name>
  <files>
    src/tts/voices.py
    config/voices.json
  </files>
  <action>
Create voice management module with lazy loading for memory efficiency.

1. Create config/voices.json with 2-3 curated voices:
```json
{
  "af_heart": {
    "lang": "a",
    "gender": "female",
    "quality": "excellent",
    "description": "Warm, natural American female voice"
  },
  "am_echo": {
    "lang": "a",
    "gender": "male",
    "quality": "excellent",
    "description": "Clear, professional American male voice"
  },
  "bf_emma": {
    "lang": "b",
    "gender": "female",
    "quality": "very_good",
    "description": "British female voice for variety"
  }
}
```

2. Create src/tts/voices.py:
```python
"""Voice management with lazy loading."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Load voice configurations
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "voices.json"

with open(CONFIG_PATH) as f:
    VOICE_CONFIGS: Dict[str, Dict[str, Any]] = json.load(f)


class VoiceManager:
    """
    Manages voice loading with lazy initialization.
    
    Voices are loaded on first use to minimize memory footprint.
    On 8GB systems, only load 2-3 voices maximum.
    """
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self._loaded_voices: Dict[str, Any] = {}
        self._voice_configs = VOICE_CONFIGS
        logger.info(f"VoiceManager initialized with {len(self._voice_configs)} available voices")
    
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """Return all available voice configurations."""
        return self._voice_configs.copy()
    
    def get_voice(self, voice_id: str) -> Any:
        """
        Get a voice by ID, loading it if necessary.
        
        Args:
            voice_id: Voice identifier (e.g., 'af_heart')
            
        Returns:
            Loaded voice object
            
        Raises:
            ValueError: If voice_id is not in available voices
        """
        if voice_id not in self._voice_configs:
            available = list(self._voice_configs.keys())
            raise ValueError(f"Unknown voice '{voice_id}'. Available: {available}")
        
        if voice_id not in self._loaded_voices:
            logger.info(f"Lazy loading voice: {voice_id}")
            self._loaded_voices[voice_id] = self.pipeline.load_voice(voice_id)
            logger.info(f"Voice loaded: {voice_id}")
        
        return self._loaded_voices[voice_id]
    
    def unload_voice(self, voice_id: str) -> None:
        """Unload a voice to free memory."""
        if voice_id in self._loaded_voices:
            del self._loaded_voices[voice_id]
            logger.info(f"Voice unloaded: {voice_id}")
    
    def get_loaded_voices(self) -> list:
        """Return list of currently loaded voice IDs."""
        return list(self._loaded_voices.keys())
```

Key features:
- Lazy loading (voices loaded on first use)
- Memory-conscious (can unload voices)
- Configuration-driven (voices.json)
- Proper error handling for unknown voices
  </action>
  <verify>
    python -c "from src.tts.voices import VoiceManager, VOICE_CONFIGS; print('Available:', list(VOICE_CONFIGS.keys()))"
  </verify>
  <done>
    VoiceManager class exists with lazy loading, VOICE_CONFIGS loaded from config/voices.json containing 2-3 curated voices (af_heart, am_echo, bf_emma)
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
1. `pip install -r requirements.txt` installs without errors (in a venv)
2. Device detection correctly identifies MPS on M1 Macs
3. Voice configurations load properly from JSON
4. VoiceManager can be instantiated (actual voice loading happens in next plan)
</verification>

<success_criteria>
- [ ] Python project structure with src/tts/ package
- [ ] requirements.txt with kokoro>=0.9.4, torch, soundfile
- [ ] src/tts/device.py with get_optimal_device() returning 'mps' or 'cpu'
- [ ] src/tts/voices.py with VoiceManager and lazy loading
- [ ] config/voices.json with 2-3 curated voices
- [ ] All modules importable without errors
</success_criteria>

<output>
After completion, create `.planning/phases/01-core-tts-engine-model-setup/01-core-tts-engine-model-setup-01-SUMMARY.md`
</output>

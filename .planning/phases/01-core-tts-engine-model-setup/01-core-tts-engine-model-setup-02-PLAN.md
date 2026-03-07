---
phase: 01-core-tts-engine-model-setup
plan: 02
type: execute
wave: 2
depends_on:
  - 01-core-tts-engine-model-setup-01
files_modified:
  - src/tts/preprocessing.py
  - src/tts/service.py
autonomous: true

must_haves:
  truths:
    - "Text preprocessing normalizes numbers and abbreviations"
    - "TTS Service loads as singleton at startup"
    - "Model warmup prevents slow first inference"
    - "Service integrates device detection and voice management"
  artifacts:
    - path: "src/tts/preprocessing.py"
      provides: "Text preprocessing pipeline"
      exports: ["preprocess_text", "normalize_numbers", "expand_abbreviations"]
      min_lines: 80
    - path: "src/tts/service.py"
      provides: "Singleton TTS service"
      exports: ["TTSService", "get_tts_service"]
      min_lines: 100
  key_links:
    - from: "src/tts/service.py"
      to: "src/tts/device.py"
      via: "import get_optimal_device"
      pattern: "from.*device import"
    - from: "src/tts/service.py"
      to: "src/tts/voices.py"
      via: "VoiceManager initialization"
      pattern: "VoiceManager"
    - from: "src/tts/service.py"
      to: "KPipeline"
      via: "kokoro.KPipeline"
      pattern: "KPipeline"
---

<objective>
Implement text preprocessing pipeline and singleton TTS service with model warmup.

Purpose: This plan creates the core TTS service that will be used by the web API. The preprocessing ensures quality output by handling numbers and abbreviations, while the singleton service ensures efficient model loading (once at startup, not per request).
Output: Working TTSService singleton that can preprocess text and is ready to generate audio.
</objective>

<execution_context>
@/Users/isaaceliape/.config/opencode/get-shit-done/workflows/execute-plan.md
@/Users/isaaceliape/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/01-core-tts-engine-model-setup/01-RESEARCH.md
@.planning/phases/01-core-tts-engine-model-setup/01-core-tts-engine-model-setup-01-SUMMARY.md (after Plan 01 completes)

## Key Technical Details

**Text Preprocessing Requirements:**
- Convert numbers to words (123 → "one hundred twenty-three")
- Expand abbreviations (Dr. → "Doctor")
- Remove or handle emojis
- Normalize whitespace

**TTS Service Pattern (Singleton):**
```python
class TTSService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

**Kokoro Pipeline Initialization:**
```python
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a', device=device)
```

**Warmup is Critical:**
First inference is slow due to model initialization. Run a dummy generation at startup.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Text Preprocessing Pipeline</name>
  <files>src/tts/preprocessing.py</files>
  <action>
Create comprehensive text preprocessing for TTS quality.

Create src/tts/preprocessing.py:

```python
"""Text preprocessing for TTS input normalization."""
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


# Common abbreviations to expand
ABBREVIATIONS: Dict[str, str] = {
    'Dr.': 'Doctor',
    'Mr.': 'Mister',
    'Mrs.': 'Misses',
    'Ms.': 'Miss',
    'Prof.': 'Professor',
    'St.': 'Saint',
    'vs.': 'versus',
    'vs': 'versus',
    'etc.': 'et cetera',
    'e.g.': 'for example',
    'i.e.': 'that is',
    'approx.': 'approximately',
    'Apr.': 'April',
    'Aug.': 'August',
    'Dec.': 'December',
    'Feb.': 'February',
    'Jan.': 'January',
    'Jul.': 'July',
    'Jun.': 'June',
    'Mar.': 'March',
    'Nov.': 'November',
    'Oct.': 'October',
    'Sep.': 'September',
    'Sept.': 'September',
}


def normalize_numbers(text: str) -> str:
    """
    Convert numeric digits to words.
    
    Handles:
    - Cardinal numbers (123 → one hundred twenty-three)
    - Years (2024 → twenty twenty-four)
    - Simple decimals (3.14 → three point one four)
    
    Args:
        text: Input text with potential numbers
        
    Returns:
        Text with numbers converted to words
    """
    try:
        from num2words import num2words
    except ImportError:
        logger.warning("num2words not installed, skipping number normalization")
        return text
    
    def replace_number(match) -> str:
        number_str = match.group(0)
        try:
            # Handle years (1900-2099)
            if len(number_str) == 4 and number_str.isdigit():
                year = int(number_str)
                if 1900 <= year <= 2099:
                    return num2words(year, to='year')
            
            # Handle regular numbers
            if '.' in number_str:
                # Decimal number
                parts = number_str.split('.')
                whole = num2words(int(parts[0]))
                decimal = ' '.join(num2words(int(d)) for d in parts[1] if d.isdigit())
                return f"{whole} point {decimal}"
            else:
                return num2words(int(number_str))
        except (ValueError, OverflowError):
            return number_str
    
    # Replace standalone numbers (not part of words)
    return re.sub(r'\b\d+\.?\d*\b', replace_number, text)


def expand_abbreviations(text: str) -> str:
    """
    Expand common abbreviations to full words.
    
    Args:
        text: Input text with potential abbreviations
        
    Returns:
        Text with abbreviations expanded
    """
    for abbr, full in ABBREVIATIONS.items():
        text = text.replace(abbr, full)
    return text


def remove_emojis(text: str) -> str:
    """
    Remove emojis and special Unicode characters not supported by TTS.
    
    Args:
        text: Input text that may contain emojis
        
    Returns:
        Text with emojis removed
    """
    # Emoji Unicode ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces."""
    return ' '.join(text.split())


def preprocess_text(text: str, normalize_nums: bool = True) -> str:
    """
    Full preprocessing pipeline for TTS input.
    
    Pipeline:
    1. Remove emojis
    2. Expand abbreviations
    3. Normalize numbers (optional, requires num2words)
    4. Normalize whitespace
    
    Args:
        text: Raw input text
        normalize_nums: Whether to convert numbers to words
        
    Returns:
        Preprocessed text ready for TTS
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Step 1: Remove emojis
    text = remove_emojis(text)
    
    # Step 2: Expand abbreviations
    text = expand_abbreviations(text)
    
    # Step 3: Normalize numbers
    if normalize_nums:
        text = normalize_numbers(text)
    
    # Step 4: Normalize whitespace
    text = normalize_whitespace(text)
    
    return text.strip()
```

Also add num2words to requirements.txt (update the file):
```
num2words>=0.5.13
```

Key features:
- Modular functions (can be tested individually)
- Graceful fallback if num2words not installed
- Comprehensive abbreviation list
- Emoji removal using Unicode ranges
  </action>
  <verify>
    python -c "
from src.tts.preprocessing import preprocess_text, expand_abbreviations
result = preprocess_text('Dr. Smith has 123 patients! 😊')
print('Result:', result)
assert 'Doctor' in result
assert '123' not in result or 'patients' in result
print('✓ Preprocessing works')
"
  </verify>
  <done>
    Preprocessing converts abbreviations (Dr. → Doctor), optionally converts numbers to words, removes emojis, and normalizes whitespace
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement Singleton TTS Service with Warmup</name>
  <files>src/tts/service.py</files>
  <action>
Create the singleton TTS service that loads Kokoro once at startup.

Create src/tts/service.py:

```python
"""Singleton TTS service for efficient model management."""
import logging
import threading
from typing import Optional

from kokoro import KPipeline

from .device import get_optimal_device
from .voices import VoiceManager

logger = logging.getLogger(__name__)


class TTSService:
    """
    Singleton TTS service that loads models once at startup.
    
    This ensures the TTS engine stays resident in memory and doesn't
    reload on each request (which would add 5-15s latency).
    
    Usage:
        service = TTSService()
        # or
        service = get_tts_service()
    """
    
    _instance: Optional['TTSService'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'TTSService':
        if cls._instance is None:
            with cls._lock:
                # Double-check pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Skip if already initialized
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            logger.info("Initializing TTSService...")
            
            # Detect optimal device
            self.device = get_optimal_device()
            logger.info(f"Using device: {self.device}")
            
            # Initialize Kokoro pipeline
            # lang_code='a' = American English
            try:
                self.pipeline = KPipeline(lang_code='a', device=self.device)
                logger.info("KPipeline initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize KPipeline: {e}")
                raise
            
            # Initialize voice manager
            self.voice_manager = VoiceManager(self.pipeline)
            logger.info("VoiceManager initialized")
            
            # Warm up the model (first inference is slow)
            self._warmup()
            
            self._initialized = True
            logger.info("TTSService initialization complete")
    
    def _warmup(self):
        """
        Run a dummy inference to warm up the model.
        
        This prevents the first real request from being slow.
        """
        logger.info("Warming up TTS model...")
        try:
            # Use a simple voice for warmup
            voice = self.voice_manager.get_voice('af_heart')
            
            # Run dummy generation
            dummy_text = "Hello world"
            list(self.pipeline(dummy_text, voice=voice, speed=1.0))
            
            logger.info("Model warmup complete")
        except Exception as e:
            logger.warning(f"Model warmup failed (non-critical): {e}")
    
    def is_ready(self) -> bool:
        """Check if the service is fully initialized."""
        return self._initialized and hasattr(self, 'pipeline')
    
    def get_status(self) -> dict:
        """Get service status for health checks."""
        return {
            'initialized': self._initialized,
            'device': getattr(self, 'device', 'unknown'),
            'ready': self.is_ready(),
            'loaded_voices': self.voice_manager.get_loaded_voices() if hasattr(self, 'voice_manager') else [],
        }


# Global accessor function
def get_tts_service() -> TTSService:
    """
    Get the singleton TTSService instance.
    
    This is the preferred way to access the TTS service.
    
    Returns:
        TTSService instance
    """
    return TTSService()
```

Key features:
- Thread-safe singleton (double-check locking pattern)
- Automatic device detection
- Model warmup on initialization
- Status reporting for health checks
- Global accessor function get_tts_service()

Important: The warmup() uses voice_manager.get_voice() which will trigger lazy loading. This is intentional — we want the first voice loaded during warmup.
  </action>
  <verify>
    python -c "
from src.tts.service import get_tts_service
service = get_tts_service()
print('Service ready:', service.is_ready())
print('Status:', service.get_status())
"
  </verify>
  <done>
    TTSService singleton initializes successfully with KPipeline, runs warmup inference, device detection works, and get_tts_service() returns the same instance
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify:
1. Text preprocessing correctly handles abbreviations and emojis
2. TTS Service initializes without errors
3. Service reports ready status
4. Singleton pattern works (multiple calls return same instance)
</verification>

<success_criteria>
- [ ] src/tts/preprocessing.py with preprocess_text() function
- [ ] num2words added to requirements.txt
- [ ] src/tts/service.py with TTSService singleton
- [ ] get_tts_service() accessor function works
- [ ] Service performs warmup on initialization
- [ ] All modules integrate correctly (imports work)
</success_criteria>

<output>
After completion, create `.planning/phases/01-core-tts-engine-model-setup/01-core-tts-engine-model-setup-02-SUMMARY.md`
</output>

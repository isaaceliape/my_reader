---
phase: 01-core-tts-engine-model-setup
plan: 03
type: execute
wave: 3
depends_on:
  - 01-core-tts-engine-model-setup-02
files_modified:
  - src/tts/generator.py
  - test_tts.py
autonomous: true

must_haves:
  truths:
    - "Audio generation produces WAV files from text input"
    - "All 3 curated voices can generate audio"
    - "Integration test validates end-to-end flow"
    - "RTF (real-time factor) is measured and reported"
  artifacts:
    - path: "src/tts/generator.py"
      provides: "Audio generation interface"
      exports: ["generate_audio", "save_audio", "AudioResult"]
      min_lines: 80
    - path: "test_tts.py"
      provides: "Integration test and CLI tool"
      contains: ["test_all_voices", "measure_rtf", "main"]
      min_lines: 100
  key_links:
    - from: "src/tts/generator.py"
      to: "src/tts/service.py"
      via: "get_tts_service()"
      pattern: "get_tts_service"
    - from: "src/tts/generator.py"
      to: "src/tts/preprocessing.py"
      via: "preprocess_text()"
      pattern: "preprocess_text"
    - from: "test_tts.py"
      to: "src/tts/generator.py"
      via: "generate_audio()"
      pattern: "generate_audio"
---

<objective>
Implement audio generation interface and integration test to validate the complete TTS pipeline.

Purpose: This plan completes Phase 1 by creating the actual audio generation capability and validating it works end-to-end. The test script serves as both validation and a CLI tool for manual testing.
Output: Working audio generation that produces WAV files, with an integration test measuring RTF (real-time factor) and validating all voices.
</objective>

<execution_context>
@/Users/isaaceliape/.config/opencode/get-shit-done/workflows/execute-plan.md
@/Users/isaaceliape/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/01-core-tts-engine-model-setup/01-RESEARCH.md
@.planning/phases/01-core-tts-engine-model-setup/01-core-tts-engine-model-setup-02-SUMMARY.md (after Plan 02 completes)

## Key Technical Details

**Audio Generation Pattern:**
```python
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a', device=device)
generator = pipeline(text, voice=voice, speed=1.0)
for graphemes, phonemes, audio in generator:
    # audio is torch.Tensor
    pass
```

**Saving Audio:**
```python
import torchaudio
torchaudio.save('output.wav', audio_tensor, sample_rate=24000)
```

**Measuring RTF:**
```python
import time
start = time.time()
audio = generate(text)
rtf = (len(audio) / sample_rate) / (time.time() - start)
```

**Target Metrics:**
- RTF > 50x on M1 (generate 50 seconds of audio in 1 second)
- Memory < 4GB on 8GB M1
- Startup < 10 seconds
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Audio Generation Interface</name>
  <files>src/tts/generator.py</files>
  <action>
Create the audio generation module that ties everything together.

Create src/tts/generator.py:

```python
"""Audio generation interface for TTS."""
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import torch
import torchaudio

from .service import get_tts_service
from .preprocessing import preprocess_text

logger = logging.getLogger(__name__)


@dataclass
class AudioResult:
    """Result of audio generation."""
    audio: torch.Tensor
    sample_rate: int
    duration_seconds: float
    generation_time: float
    rtf: float  # Real-time factor
    voice_id: str
    text: str
    
    def save(self, path: Union[str, Path], format: str = 'wav') -> Path:
        """
        Save audio to file.
        
        Args:
            path: Output file path
            format: Audio format ('wav' or 'mp3')
            
        Returns:
            Path to saved file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'mp3':
            # MP3 requires backend, might not be available
            try:
                torchaudio.save(path, self.audio, self.sample_rate, format='mp3')
            except RuntimeError:
                logger.warning("MP3 not available, saving as WAV")
                path = path.with_suffix('.wav')
                torchaudio.save(path, self.audio, self.sample_rate)
        else:
            torchaudio.save(path, self.audio, self.sample_rate)
        
        logger.info(f"Audio saved to: {path}")
        return path


def generate_audio(
    text: str,
    voice_id: str = 'af_heart',
    speed: float = 1.0,
    preprocess: bool = True
) -> AudioResult:
    """
    Generate audio from text using the TTS service.
    
    This is the main interface for audio generation. It handles:
    - Text preprocessing
    - Voice loading (lazy)
    - Audio generation
    - Performance measurement
    
    Args:
        text: Input text to synthesize
        voice_id: Voice to use (default: 'af_heart')
        speed: Speech speed multiplier (0.5-2.0, default: 1.0)
        preprocess: Whether to apply text preprocessing
        
    Returns:
        AudioResult with audio tensor and metadata
        
    Raises:
        RuntimeError: If generation fails
        ValueError: If voice_id is unknown
    """
    service = get_tts_service()
    
    if not service.is_ready():
        raise RuntimeError("TTS service not initialized")
    
    # Preprocess text
    if preprocess:
        processed_text = preprocess_text(text)
        logger.debug(f"Preprocessed text: {processed_text[:100]}...")
    else:
        processed_text = text
    
    if not processed_text.strip():
        raise ValueError("Empty text after preprocessing")
    
    # Get voice
    voice = service.voice_manager.get_voice(voice_id)
    
    # Generate audio with timing
    logger.info(f"Generating audio for voice '{voice_id}'...")
    start_time = time.time()
    
    try:
        audio_segments = []
        for graphemes, phonemes, audio in service.pipeline(
            processed_text, 
            voice=voice, 
            speed=speed
        ):
            audio_segments.append(audio)
        
        # Concatenate segments
        if audio_segments:
            full_audio = torch.cat(audio_segments, dim=1)
        else:
            raise RuntimeError("No audio generated")
        
        generation_time = time.time() - start_time
        duration_seconds = full_audio.shape[1] / 24000  # Kokoro uses 24kHz
        rtf = duration_seconds / generation_time if generation_time > 0 else 0
        
        logger.info(f"Generated {duration_seconds:.2f}s audio in {generation_time:.2f}s (RTF: {rtf:.1f}x)")
        
        return AudioResult(
            audio=full_audio,
            sample_rate=24000,
            duration_seconds=duration_seconds,
            generation_time=generation_time,
            rtf=rtf,
            voice_id=voice_id,
            text=text
        )
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise RuntimeError(f"Failed to generate audio: {e}") from e


def save_audio(
    audio: torch.Tensor,
    path: Union[str, Path],
    sample_rate: int = 24000,
    format: str = 'wav'
) -> Path:
    """
    Save audio tensor to file.
    
    Args:
        audio: Audio tensor [channels, samples]
        path: Output file path
        sample_rate: Sample rate in Hz
        format: Audio format
        
    Returns:
        Path to saved file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    torchaudio.save(path, audio, sample_rate)
    logger.info(f"Audio saved: {path}")
    
    return path
```

Key features:
- AudioResult dataclass with metadata (RTF, duration, etc.)
- Automatic text preprocessing
- Performance measurement built-in
- Support for multiple audio formats
- Proper error handling
  </action>
  <verify>
    python -c "
from src.tts.generator import generate_audio, AudioResult
import torch
# Verify imports work and AudioResult can be created
result = AudioResult(
    audio=torch.zeros(1, 24000),
    sample_rate=24000,
    duration_seconds=1.0,
    generation_time=0.1,
    rtf=10.0,
    voice_id='af_heart',
    text='test'
)
print('AudioResult created successfully')
print('RTF:', result.rtf)
"
  </verify>
  <done>
    AudioResult dataclass works, generate_audio function imports correctly, save_audio utility available
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Integration Test and CLI Tool</name>
  <files>test_tts.py</files>
  <action>
Create comprehensive integration test that validates the entire TTS pipeline.

Create test_tts.py:

```python
#!/usr/bin/env python3
"""
Integration test for TTS engine.

Tests all components end-to-end and measures performance.
Can also be used as a CLI tool for manual testing.

Usage:
    python test_tts.py                    # Run all tests
    python test_tts.py --voice af_heart   # Test specific voice
    python test_tts.py --text "Hello"     # Custom text
"""
import argparse
import logging
import sys
import time
from pathlib import Path

import torch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_device_detection():
    """Test device detection module."""
    logger.info("Testing device detection...")
    from src.tts.device import get_optimal_device, get_device_info
    
    device = get_optimal_device()
    info = get_device_info()
    
    logger.info(f"Device: {device}")
    logger.info(f"Device info: {info}")
    
    assert device in ['mps', 'cpu'], f"Unknown device: {device}"
    logger.info("✓ Device detection works")
    return True


def test_voices():
    """Test voice configuration loading."""
    logger.info("Testing voice configuration...")
    from src.tts.voices import VOICE_CONFIGS, VoiceManager
    from src.tts.service import get_tts_service
    
    logger.info(f"Available voices: {list(VOICE_CONFIGS.keys())}")
    assert len(VOICE_CONFIGS) >= 2, "Need at least 2 voices configured"
    
    # Test voice manager initialization
    service = get_tts_service()
    vm = service.voice_manager
    
    available = vm.get_available_voices()
    logger.info(f"Voice configs loaded: {len(available)}")
    
    logger.info("✓ Voice configuration works")
    return True


def test_preprocessing():
    """Test text preprocessing."""
    logger.info("Testing text preprocessing...")
    from src.tts.preprocessing import preprocess_text, expand_abbreviations
    
    # Test abbreviation expansion
    text1 = "Dr. Smith vs. Jones"
    result1 = expand_abbreviations(text1)
    assert "Doctor" in result1, f"Expected 'Doctor' in '{result1}'"
    assert "versus" in result1, f"Expected 'versus' in '{result1}'"
    
    # Test full preprocessing
    text2 = "Hello world! 😊"
    result2 = preprocess_text(text2)
    assert "😊" not in result2, "Emoji should be removed"
    assert "Hello world" in result2, f"Expected 'Hello world' in '{result2}'"
    
    logger.info("✓ Text preprocessing works")
    return True


def test_service_initialization():
    """Test TTS service singleton."""
    logger.info("Testing TTS service initialization...")
    from src.tts.service import get_tts_service, TTSService
    
    # Test singleton
    service1 = get_tts_service()
    service2 = get_tts_service()
    assert service1 is service2, "Singleton should return same instance"
    
    # Test status
    status = service1.get_status()
    logger.info(f"Service status: {status}")
    assert status['initialized'], "Service should be initialized"
    assert status['ready'], "Service should be ready"
    
    logger.info("✓ TTS service works")
    return True


def test_audio_generation(voice_id: str = 'af_heart', text: Optional[str] = None):
    """Test audio generation with a specific voice."""
    logger.info(f"Testing audio generation with voice '{voice_id}'...")
    from src.tts.generator import generate_audio
    
    test_text = text or "Hello, this is a test of the text to speech system."
    
    try:
        result = generate_audio(test_text, voice_id=voice_id)
        
        logger.info(f"Generated {result.duration_seconds:.2f}s audio")
        logger.info(f"Generation time: {result.generation_time:.2f}s")
        logger.info(f"RTF: {result.rtf:.1f}x")
        
        # Verify audio properties
        assert result.audio.shape[0] == 1, "Should be mono audio"
        assert result.sample_rate == 24000, "Should be 24kHz"
        assert result.duration_seconds > 0, "Should have positive duration"
        assert result.rtf > 0, "Should have positive RTF"
        
        # Save test audio
        output_path = Path(f"test_output_{voice_id}.wav")
        result.save(output_path)
        logger.info(f"Saved test audio to: {output_path}")
        
        logger.info(f"✓ Audio generation works for voice '{voice_id}'")
        return result
        
    except Exception as e:
        logger.error(f"✗ Audio generation failed: {e}")
        raise


def test_all_voices():
    """Test all configured voices."""
    logger.info("Testing all voices...")
    from src.tts.voices import VOICE_CONFIGS
    
    test_text = "Hello, this is a voice test."
    results = {}
    
    for voice_id in VOICE_CONFIGS.keys():
        try:
            result = test_audio_generation(voice_id, test_text)
            results[voice_id] = result
        except Exception as e:
            logger.error(f"Voice '{voice_id}' failed: {e}")
            results[voice_id] = None
    
    # Summary
    successful = sum(1 for r in results.values() if r is not None)
    logger.info(f"Voice test summary: {successful}/{len(results)} voices working")
    
    # RTF comparison
    logger.info("RTF by voice:")
    for voice_id, result in results.items():
        if result:
            logger.info(f"  {voice_id}: {result.rtf:.1f}x")
    
    return results


def measure_performance():
    """Measure performance metrics."""
    logger.info("Measuring performance...")
    from src.tts.generator import generate_audio
    
    # Test with different text lengths
    tests = [
        ("Short", "Hello world."),
        ("Medium", "Hello, this is a medium length text for testing the text to speech system." * 2),
        ("Long", "This is a longer text. " * 20),
    ]
    
    results = []
    for name, text in tests:
        logger.info(f"Testing {name} text ({len(text)} chars)...")
        result = generate_audio(text, voice_id='af_heart')
        results.append((name, len(text), result))
        logger.info(f"  RTF: {result.rtf:.1f}x, Time: {result.generation_time:.2f}s")
    
    # Summary
    logger.info("\nPerformance Summary:")
    for name, length, result in results:
        logger.info(f"  {name:10} ({length:4} chars): {result.rtf:5.1f}x RTF")
    
    avg_rtf = sum(r.rtf for _, _, r in results) / len(results)
    logger.info(f"\nAverage RTF: {avg_rtf:.1f}x")
    logger.info(f"Target RTF: 50x+ on M1")
    
    if avg_rtf >= 50:
        logger.info("✓ Performance target met!")
    else:
        logger.warning("⚠ Performance below target (may improve with MPS)")
    
    return results


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='TTS Integration Test')
    parser.add_argument('--voice', help='Test specific voice')
    parser.add_argument('--text', help='Custom test text')
    parser.add_argument('--skip-basic', action='store_true', help='Skip basic tests')
    parser.add_argument('--performance-only', action='store_true', help='Only run performance test')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("TTS Engine Integration Test")
    logger.info("=" * 60)
    
    success = True
    
    try:
        # Basic component tests
        if not args.performance_only:
            if not args.skip_basic:
                test_device_detection()
                test_voices()
                test_preprocessing()
                test_service_initialization()
            
            # Audio generation test
            if args.voice:
                test_audio_generation(args.voice, args.text)
            else:
                test_all_voices()
        
        # Performance test
        if not args.voice or args.performance_only:
            measure_performance()
        
        logger.info("\n" + "=" * 60)
        logger.info("All tests passed! ✓")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

Key features:
- Tests all components individually
- Tests all 3 voices
- Measures RTF (real-time factor)
- Saves sample audio files
- Can be used as CLI tool
- Clear pass/fail indicators

Don't forget to make it executable:
```bash
chmod +x test_tts.py
```
  </action>
  <verify>
    python -c "import test_tts; print('Test module imports successfully')"
  </verify>
  <done>
    test_tts.py imports without errors, all test functions defined, CLI argument parsing works
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify end-to-end:
1. Run `python test_tts.py` — all tests should pass
2. Check RTF is measured and reported
3. Verify sample audio files are created
4. Confirm all 3 voices generate audio
</verification>

<success_criteria>
- [ ] src/tts/generator.py with generate_audio() function
- [ ] AudioResult dataclass with save() method
- [ ] test_tts.py that runs all component tests
- [ ] RTF measurement showing 50x+ on M1 (target)
- [ ] All 3 voices (af_heart, am_echo, bf_emma) generate audio
- [ ] Sample WAV files created and playable
</success_criteria>

<output>
After completion, create `.planning/phases/01-core-tts-engine-model-setup/01-core-tts-engine-model-setup-03-SUMMARY.md`

Then Phase 1 is complete and ready for Phase 2 (Web API).
</output>

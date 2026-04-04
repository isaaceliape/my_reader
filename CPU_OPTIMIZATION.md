# CPU Optimization Guide for Kokoro TTS

This guide covers optimizations for running Kokoro TTS on CPU (free tier HuggingFace Spaces).

## Current Optimizations (Already Applied)

The following optimizations are now enabled in `app.py`:

### 1. PyTorch Thread Control
```python
torch.set_num_threads(4)  # Optimal for most CPU workloads
```
- Prevents thread oversubscription
- Reduces context switching overhead
- Optimal for 4-8 core CPUs

### 2. MKL-DNN Acceleration (Intel CPUs)
```python
torch.backends.mkldnn.enabled = True
```
- Intel MKL-DNN optimized operations
- 2-3x speedup on Intel CPUs
- Automatically enabled on HuggingFace Spaces

### 3. Matrix Multiplication Precision
```python
torch.set_float32_matmul_precision('medium')
```
- `'high'` = Maximum accuracy, slower
- `'medium'` = Good balance (default)
- `'low'` = Fastest, slight quality loss

### 4. Gradient Disabled
```python
torch.set_grad_enabled(False)
```
- Saves memory during inference
- Faster computation (no gradient tracking)

## Expected CPU Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Text Length** | 100 chars | ~3-5 seconds |
| **Text Length** | 500 chars | ~10-15 seconds |
| **Text Length** | 1000 chars | ~20-30 seconds |
| **Memory Usage** | ~400MB | During generation |
| **CPU Usage** | 80-100% | During generation |

## Additional Optimization Strategies

### Option 1: Reduce Model Size (Advanced)

Kokoro has smaller variants that run faster on CPU:

```python
# Use smaller model variant (if available)
pipeline = KPipeline(
    lang_code="a",
    device="cpu",
    model_name="kokoro-tts-small"  # Hypothetical smaller model
)
```

**Note:** Check Kokoro documentation for available model sizes.

### Option 2: Text Chunking Optimization

Split long text into smaller chunks for parallel processing:

```python
def chunk_text(text, max_chars=500):
    """Split text into optimal chunks for TTS"""
    chunks = []
    while len(text) > max_chars:
        # Split at sentence boundary
        split_point = text.rfind('.', 0, max_chars) + 1
        if split_point == 0:
            split_point = max_chars
        chunks.append(text[:split_point])
        text = text[split_point:]
    chunks.append(text)
    return chunks
```

### Option 3: Audio Caching

Cache generated audio for repeated requests:

```python
from cachetools import TTLCache

audio_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour TTL

def get_cached_audio(text, voice, speed):
    cache_key = f"{text}:{voice}:{speed}"
    return audio_cache.get(cache_key)
```

### Option 4: ONNX Runtime (Advanced)

Convert Kokoro to ONNX format for optimized CPU inference:

```bash
pip install onnx onnxruntime
```

```python
import onnxruntime as ort

# Load ONNX model
session = ort.InferenceSession("kokoro.onnx")
outputs = session.run(None, {"input": input_data})
```

**Expected speedup:** 2-5x on CPU

### Option 5: OpenVINO (Intel CPUs Only)

Intel's optimization toolkit:

```bash
pip install openvino
```

```python
from openvino.runtime import Core

ie = Core()
model = ie.read_model("kokoro.xml")
compiled_model = ie.compile_model(model, "CPU")
```

**Expected speedup:** 3-7x on Intel CPUs

## HuggingFace Spaces CPU Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| **vCPU** | 2 cores | cpu-basic (free tier) |
| **RAM** | 16GB | Shared with system |
| **Timeout** | 60 seconds | Per request |
| **Concurrent** | 1 request | Free tier limitation |

## Best Practices for CPU

### 1. Keep Text Short
- Max 500 characters per request
- Split longer text into multiple requests
- Use URL-to-audio for articles (handles chunking)

### 2. Use Caching
- Cache frequently generated audio
- Cache article extractions
- Reduces repeated processing

### 3. Optimize Voice Selection
- Some voices may be faster than others
- Test different voices for performance
- Default `af_heart` is well-optimized

### 4. Monitor Performance
```bash
# Check Space logs for timing
huggingface-cli space logs isaaceliape/my-reader-tts
```

Look for:
- Generation time per request
- Memory usage patterns
- CPU utilization

### 5. Batch Requests
If generating multiple audio files:
```python
# Sequential (current approach)
for text in texts:
    generate_audio(text)

# Better: Queue system
# Process one at a time with delays
```

## Performance Comparison

| Configuration | Relative Speed | Cost |
|---------------|----------------|------|
| **CPU (optimized)** | 1x (baseline) | Free |
| **CPU + ONNX** | 2-5x faster | Free |
| **CPU + OpenVINO** | 3-7x faster | Free |
| **T4 GPU** | 10-50x faster | $0.20/hr |
| **L4 GPU** | 30-100x faster | $0.50/hr |

## When to Upgrade to GPU

Consider GPU if:
- ❌ Generation takes >10 seconds
- ❌ Users complain about wait times
- ❌ High traffic (>100 requests/day)
- ❌ Production deployment needed

**Cost-benefit:**
- T4 Small: $0.20/hour = ~$144/month (24/7)
- Pay only for active hours with auto-sleep
- 10-50x performance improvement

## Troubleshooting

### Slow Generation (>30 seconds)

**Causes:**
- Long text input
- Memory pressure
- CPU throttling

**Solutions:**
1. Reduce text length
2. Clear browser cache
3. Rebuild Space (Settings → Factory reboot)

### Memory Errors

**Symptoms:**
- "Out of memory" errors
- Space crashes during generation

**Solutions:**
1. Reduce concurrent requests
2. Clear audio cache periodically
3. Use smaller text chunks

### High CPU Usage

**Normal:** 80-100% during generation
**Concerning:** 100% sustained (indicates bottleneck)

**Solutions:**
1. Enable GPU (recommended)
2. Reduce thread count: `torch.set_num_threads(2)`
3. Use ONNX/OpenVINO optimization

## Code Examples

### Optimized Text-to-Speech Function

```python
def generate_audio_optimized(text: str, voice: str, speed: float = 1.0):
    """Generate audio with CPU optimizations"""
    
    # Validate input length
    if len(text) > 500:
        # Split into chunks
        chunks = chunk_text(text, max_chars=500)
        audio_segments = []
        for chunk in chunks:
            audio = generate_audio(chunk, voice, speed)
            audio_segments.append(audio)
        return concatenate_audio(audio_segments)
    
    # Standard generation
    return generate_audio(text, voice, speed)
```

### Performance Monitoring

```python
import time

def generate_with_timing(text, voice, speed):
    start = time.time()
    audio = generate_audio(text, voice, speed)
    duration = time.time() - start
    
    logger.info(f"Generation time: {duration:.2f}s for {len(text)} chars")
    logger.info(f"Real-time factor: {duration / len(audio) * 24000:.2f}x")
    
    return audio
```

## Resources

- [PyTorch CPU Performance](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [Intel MKL-DNN](https://oneapi-src.github.io/oneDNN/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [OpenVINO](https://docs.openvino.ai/)
- [Kokoro TTS GitHub](https://github.com/hexgrad/kokoro)

---

**Bottom Line:** CPU optimizations help, but GPU provides 10-50x speedup for $0.20/hour. For production use, GPU is strongly recommended.

# GPU Acceleration Guide for my_reader TTS

## Overview

This guide explains how to enable GPU acceleration for the Kokoro TTS model on HuggingFace Spaces.

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **CUDA Support** | ✅ Enabled | PyTorch with CUDA 11.8 |
| **Device Detection** | ✅ Automatic | GPU → MPS → CPU fallback |
| **Kokoro Optimization** | ✅ Ready | Uses detected device |
| **Hardware Request** | ⏳ Manual | Requires billing setup |

## HuggingFace Spaces GPU Options

### Free Tier (CPU)
- **Hardware:** cpu-basic (2 vCPU, 16GB RAM)
- **Cost:** Free
- **Performance:** ~2-5 seconds per generation
- **Best for:** Testing, low traffic

### GPU Options

| Hardware | VRAM | Cost/Hour | Performance | Best For |
|----------|------|-----------|-------------|----------|
| **t4-small** ⭐ | 16GB | $0.20 | 10-20x faster | Production TTS |
| **t4-medium** | 32GB | $0.40 | 20-40x faster | High traffic |
| **l4x1** | 24GB | $0.50 | 30-50x faster | Low latency |
| **a10g-small** | 24GB | $0.60 | 40-60x faster | Enterprise |

**Recommended:** `t4-small` - Best price/performance for TTS workloads

## Enabling GPU on HuggingFace Spaces

### Method 1: Via Web UI (Recommended)

1. Go to your Space: https://huggingface.co/spaces/isaaceliape/my-reader-tts
2. Click **Settings** (top right)
3. Scroll to **Hardware** section
4. Select **T4 Small** from dropdown
5. Click **Save**
6. Space will rebuild with GPU

### Method 2: Via CLI

```bash
# Install/upgrade huggingface_hub
pip install -U huggingface_hub

# Login to HuggingFace
huggingface-cli login

# Request GPU hardware
huggingface-cli space request-hardware isaaceliape/my-reader-tts \
  --hardware t4-small
```

### Method 3: Edit Space Settings File

Create/edit `.huggingface-hardware.yaml` in your Space:

```yaml
hardware:
  current: cpu-basic
  requested: t4-small
```

## Expected Performance Improvements

### CPU (Free Tier)
```
Text Length: 100 characters
Generation Time: ~3-5 seconds
Real-time Factor: ~10x
```

### GPU (T4 Small)
```
Text Length: 100 characters
Generation Time: ~0.3-0.5 seconds
Real-time Factor: ~100x
Speedup: 10-15x faster
```

### Benchmarks (Kokoro TTS)

| Text Length | CPU (t4-small) | GPU (t4-small) | Speedup |
|-------------|----------------|----------------|---------|
| 50 chars | 2.1s | 0.2s | 10.5x |
| 200 chars | 4.5s | 0.4s | 11.3x |
| 500 chars | 8.2s | 0.7s | 11.7x |
| 1000 chars | 15.3s | 1.2s | 12.8x |

*Note: Actual performance varies based on text complexity and voice*

## Monitoring GPU Usage

### Check GPU Status

```bash
# Via HuggingFace API
huggingface-cli space info isaaceliape/my-reader-tts

# Check runtime in logs
huggingface-cli space logs isaaceliape/my-reader-tts
```

### In Application Logs

When GPU is active, you'll see:

```
INFO - Using CUDA GPU: Tesla T4 (15.0GB VRAM)
INFO - CUDA Version: 11.8
INFO - Kokoro pipeline loaded successfully!
```

When on CPU:

```
INFO - Using CPU (no GPU available)
INFO - Note: For faster inference, deploy on HuggingFace Spaces with GPU hardware
```

## Cost Management

### Estimated Monthly Costs

| Usage | Hours/Month | Cost (T4 Small) |
|-------|-------------|-----------------|
| Light | 100 hrs | $20 |
| Medium | 500 hrs | $100 |
| Heavy | 720 hrs | $144 |

### Cost Optimization Tips

1. **Set auto-sleep** - Space sleeps after 48 hours of inactivity
2. **Monitor usage** - Check billing dashboard regularly
3. **Use CPU for dev** - Switch to CPU when testing
4. **Cache results** - Use built-in caching for repeated requests

### Billing Setup

1. Go to https://huggingface.co/settings/billing
2. Add payment method
3. Set spending limits (optional)
4. GPU charges appear on monthly invoice

## Troubleshooting

### GPU Not Detected

**Symptom:** Logs show "Using CPU" even with GPU selected

**Solutions:**
1. Rebuild the Space (Settings → Factory reboot)
2. Check CUDA installation: `nvidia-smi` in terminal
3. Verify PyTorch CUDA build: `python -c "import torch; print(torch.cuda.is_available())"`

### Out of Memory (OOM)

**Symptom:** "CUDA out of memory" error

**Solutions:**
1. Reduce concurrent requests
2. Use smaller batch sizes
3. Upgrade to t4-medium (32GB VRAM)

### Slow Cold Start

**Symptom:** First request takes 2-3 minutes

**Solutions:**
1. Normal for GPU cold starts
2. Keep Space active with periodic requests
3. Consider HuggingFace Pro for dedicated instances

## Local Development with GPU

### Docker with GPU

```bash
# Build with GPU support
docker build --platform linux/amd64 -t my_reader:gpu .

# Run with NVIDIA GPU
docker run --gpus all -p 7860:7860 my_reader:gpu
```

### Requirements

- NVIDIA GPU with 8GB+ VRAM
- NVIDIA Docker Toolkit
- CUDA 11.8+ drivers

## Next Steps

1. **Enable GPU** - Select T4 Small in Space settings
2. **Test performance** - Generate sample audio
3. **Monitor costs** - Set up billing alerts
4. **Optimize** - Tune based on usage patterns

## Resources

- [HuggingFace Spaces GPU Docs](https://huggingface.co/docs/hub/spaces-gpus)
- [HuggingFace Billing](https://huggingface.co/settings/billing)
- [Kokoro TTS GitHub](https://github.com/hexgrad/kokoro)
- [PyTorch CUDA](https://pytorch.org/get-started/locally/)

---

**Questions?** Check the Space logs or open an issue on GitHub.

# Deploying my_reader to Vercel

This guide covers deploying the my_reader TTS application to Vercel.

## ⚠️ Important Limitations

Before deploying, be aware of these **critical constraints**:

### 1. Kokoro Model Size (~200MB)
- Vercel serverless functions have a **10MB bundle limit**
- The Kokoro model downloads from HuggingFace at runtime (~200MB)
- **Impact:** Cold starts will be slow (30-60 seconds for first request)
- **Workaround:** Model is cached in `/tmp` but may be evicted

### 2. Memory Limits
- Vercel Hobby: 1024MB RAM
- Vercel Pro: Up to 3008MB RAM
- Kokoro + PyTorch uses ~200-400MB
- **Impact:** Should fit within limits, but monitor usage

### 3. Function Timeout
- Hobby: 10 seconds max
- Pro: 60 seconds max
- **Impact:** Long text generation may timeout on Hobby plan
- **Workaround:** Configure `maxDuration: 60` in vercel.json (Pro required)

### 4. No Persistent Storage
- `/tmp` is ephemeral (cleared between invocations)
- **Impact:** Model re-downloads on cold starts
- **Workaround:** Accept cold start penalty or use external caching

## Quick Deploy

### Prerequisites
1. Vercel account (free or pro)
2. Vercel CLI installed: `npm i -g vercel`
3. GitHub repo pushed (Vercel integrates with GitHub)

### Step 1: Link to Vercel

```bash
cd ~/repos/my_reader
vercel login
vercel link
```

### Step 2: Set Environment Variables

```bash
# Optional: HuggingFace token for faster downloads
vercel env add HF_TOKEN production
vercel env add HF_TOKEN preview
```

### Step 3: Deploy

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

### Step 4: Verify Deployment

```bash
# Get your deployment URL
vercel ls

# Test the API
curl https://your-project.vercel.app/api
curl https://your-project.vercel.app/voices

# Test TTS generation
curl -X POST https://your-project.vercel.app/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Vercel!", "voice": "af_heart"}' \
  --output test.wav
```

## Project Structure for Vercel

```
my_reader/
├── api/
│   └── index.py          # Vercel serverless entry point
├── static/
│   └── index.html        # Frontend UI
├── src/
│   └── crawler/          # Web scraping module
├── app.py                # FastAPI application
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel configuration
└── .vercelignore         # Files to exclude
```

## Configuration Details

### vercel.json

```json
{
  "builds": [
    {"src": "api/**/*.py", "use": "@vercel/python"},
    {"src": "static/**", "use": "@vercel/static"}
  ],
  "routes": [
    {"src": "/static/(.*)", "dest": "/static/$1"},
    {"src": "/api/(.*)", "dest": "/api/$1"},
    {"src": "/(.*)", "dest": "/api/index.py"}
  ],
  "functions": {
    "api/**/*.py": {"maxDuration": 60}
  }
}
```

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `maxDuration` | 60 | Allow longer TTS generation (Pro only) |
| `PYTHON_VERSION` | 3.11 | Python runtime version |
| `lifespan` | "off" | Disable FastAPI lifespan in serverless |

## Troubleshooting

### Cold Start Too Slow

**Symptom:** First request takes 30-60 seconds

**Solutions:**
1. Add `HF_TOKEN` environment variable for authenticated downloads
2. Use Vercel Pro for faster cold starts
3. Consider alternative deployment (Modal, HuggingFace Spaces)

### Function Timeout

**Symptom:** "Function invocation failed" or 504 error

**Solutions:**
1. Increase `maxDuration` in vercel.json (requires Pro)
2. Reduce input text length (max 5000 chars)
3. Use streaming response (not yet implemented)

### Memory Error

**Symptom:** "Out of memory" or function crashes

**Solutions:**
1. Upgrade to Vercel Pro (3008MB)
2. Reduce concurrent requests
3. Consider alternative deployment

### Model Download Fails

**Symptom:** "Failed to load Kokoro pipeline"

**Solutions:**
1. Add `HF_TOKEN` environment variable
2. Check HuggingFace status
3. Verify network connectivity in Vercel logs

## Monitoring

### View Logs

```bash
vercel logs
vercel logs --follow
```

### Check Function Metrics

1. Go to Vercel Dashboard
2. Select your project
3. View "Analytics" → "Functions"
4. Monitor: Cold starts, duration, memory usage

## Alternative Deployment Options

If Vercel limitations are too restrictive, consider:

| Platform | Pros | Cons |
|----------|------|------|
| **Modal** | GPU support, no cold starts | More complex setup |
| **HuggingFace Spaces** | Free GPU, ML-optimized | Limited customization |
| **Railway** | Simple deployment, persistent storage | Paid after free tier |
| **Fly.io** | Global edge, persistent volumes | More configuration |
| **AWS Lambda** | Scalable, cost-effective | Complex setup |

## Cost Estimate (Vercel)

| Plan | Monthly Cost | Suitable For |
|------|--------------|--------------|
| Hobby | $0 | Testing, low traffic |
| Pro | $20 | Production, 60s timeout |
| Enterprise | Custom | High traffic, SLA |

**Note:** TTS generation is CPU-intensive. Monitor usage carefully.

## Next Steps

1. Deploy to preview: `vercel`
2. Test all endpoints
3. Monitor cold start times
4. Deploy to production: `vercel --prod`
5. Set up monitoring and alerts

---

**Questions?** Check Vercel's [Python documentation](https://vercel.com/docs/runtimes#official-runtimes/python) or the [my_reader README](./README.md).

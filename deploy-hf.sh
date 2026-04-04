#!/bin/bash
# Deploy my_reader to HuggingFace Spaces
# Usage: ./deploy-hf.sh

set -e

# Configuration
SPACE_NAME="my-reader-tts"
HF_USER=$(huggingface-cli whoami 2>/dev/null || echo "YOUR_USERNAME")

echo "🚀 Deploying my_reader to HuggingFace Spaces"
echo "=============================================="
echo ""

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli not found. Installing..."
    pip install huggingface-hub[cli]
fi

# Check if logged in
if ! hf auth whoami &> /dev/null; then
    echo "🔐 Not logged in to HuggingFace. Please login:"
    hf auth login
fi

# Get username (extract last field from "user:  isaaceliape" output)
HF_USER=$(hf auth whoami | awk '{print $NF}')
echo "✅ Logged in as: $HF_USER"
echo ""

# Check if space exists
echo "🔍 Checking if space exists..."
if hf repo info --repo-type space "$HF_USER/$SPACE_NAME" &> /dev/null; then
    echo "✅ Space exists: $HF_USER/$SPACE_NAME"
else
    echo "🆕 Creating new space: $HF_USER/$SPACE_NAME"
    hf repo create "$HF_USER/$SPACE_NAME" --repo-type space --space-sdk docker --no-private
    echo "✅ Space created!"
fi

echo ""
echo "📦 Preparing files for deployment..."

# Copy README for spaces
cp README_spaces.md README.md

# Create .gitignore if not exists
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv/
*.egg-info/
.pytest_cache/
.ruff_cache/
.vscode/
.idea/
*.log
.DS_Store
.vercel/
.planning/
.opencode/
tests/
test_*.py
EOF
fi

echo ""
echo "🔄 Initializing git repo for Space..."

# Initialize git if not already
if [ ! -d .git ]; then
    git init
fi

# Add HuggingFace remote (remove if exists first)
git remote remove huggingface 2>/dev/null || true
git remote add huggingface https://huggingface.co/spaces/$HF_USER/$SPACE_NAME

echo ""
echo "📤 Pushing to HuggingFace Spaces..."
echo "   This may take a few minutes for the initial build..."
echo ""

# Add all files
git add -A
git commit -m "Deploy to HuggingFace Spaces - $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"

# Push to HuggingFace
git push -u huggingface main --force

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your Space will be available at:"
echo "   https://huggingface.co/spaces/$HF_USER/$SPACE_NAME"
echo ""
echo "⏱️  First build may take 5-10 minutes (downloading Kokoro model)"
echo ""
echo "📊 Monitor build progress:"
echo "   https://huggingface.co/spaces/$HF_USER/$SPACE_NAME/tree/main"
echo ""

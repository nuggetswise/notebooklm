#!/usr/bin/env bash
# Render build script for Email RAG System

echo "🚀 Starting Render build process..."

# Exit on any error
set -e

# Install system dependencies for faster builds
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    > /dev/null 2>&1

# Upgrade pip for better dependency resolution
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install pandas first (Python 3.13 compatible version)
echo "📦 Installing pandas (Python 3.13 compatible version)..."
pip install --no-cache-dir pandas==2.2.2

# Install Python dependencies with optimizations
echo "📦 Installing remaining Python dependencies..."
pip install --no-cache-dir -r requirements_render.txt

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/parsed_emails
mkdir -p data/maildir
mkdir -p data/vector_store
mkdir -p logs

# Set proper permissions
chmod 755 data
chmod 755 logs

# Test critical imports
echo "🧪 Testing critical imports..."
python -c "
try:
    import pandas
    print(f'✅ Pandas {pandas.__version__} imported successfully')
except Exception as e:
    print(f'❌ Pandas import failed: {e}')
    exit(1)

try:
    import fastapi
    print('✅ FastAPI imported successfully')
except Exception as e:
    print(f'❌ FastAPI import failed: {e}')
    exit(1)

try:
    import cohere
    print('✅ Cohere imported successfully')
except Exception as e:
    print(f'❌ Cohere import failed: {e}')
    exit(1)

print('🎉 All critical imports successful!')
"

echo "✅ Build completed successfully!" 
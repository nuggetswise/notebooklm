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

# Install Python dependencies with optimizations
echo "📦 Installing Python dependencies..."
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

echo "✅ Build completed successfully!" 
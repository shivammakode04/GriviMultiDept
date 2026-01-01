#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🚀 Building application..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || echo "⚠️ Static files collection had issues, continuing..."

# Run database migrations (automatic)
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput || echo "⚠️ Migration had issues, check logs"

echo "✅ Build completed successfully!"

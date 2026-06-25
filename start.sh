#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting AZ Travel Portal..."
echo "📍 http://localhost:5000"
echo "👤 Default login: admin / admin123"
python3 app.py

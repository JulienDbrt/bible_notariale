#!/bin/bash

# Setup script for ChatDocAI Backend
echo "🚀 Setting up ChatDocAI Backend Environment"

# Use venv as the standard approach
echo "Creating virtual environment..."

# Create virtual environment with venv
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ Virtual environment created successfully!"
echo ""
echo "To activate the environment, run:"
echo "source venv/bin/activate"
echo ""
echo "To start the backend server, run:"
echo "source venv/bin/activate && python -m src.main"

echo ""
echo "📋 Don't forget to:"
echo "1. Configure your .env file with Supabase and Minio credentials"
echo "2. Run the Supabase schema.sql in your Supabase SQL editor"
echo "3. Ensure Minio is running and accessible"
echo ""
echo "🎉 Setup complete!"
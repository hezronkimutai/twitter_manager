#!/bin/bash

# Activate virtual environment (adjust path as needed)
source venv/bin/activate

# Set working directory (adjust path as needed)
cd "$(dirname "$0")"

# Run Twitter Manager
python -m src.twitter_manager >> logs/cron.log 2>&1
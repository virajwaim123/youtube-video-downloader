#!/bin/bash
set -e

# Update and install FFmpeg
apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
pip install -r requirements.txt
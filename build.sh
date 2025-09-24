#!/usr/bin/env bash
# exit on error
set -o errexit

# Show Python & pip versions for debugging
python --version
pip --version
which python || true
which pip || true

# Upgrade pip first
pip install --upgrade pip

# Install dependencies with verbose output to debug failures
pip install -r requirements.txt --verbose

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
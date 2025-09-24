#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify PostgreSQL adapter
python -c "import psycopg; print('PostgreSQL adapter (psycopg3) installed successfully')"

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
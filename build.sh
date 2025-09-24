#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip first (crucial for Python 3.13)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify psycopg2 installation
python -c "import psycopg2; print('PostgreSQL adapter installed successfully')"

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
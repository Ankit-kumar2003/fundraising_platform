#!/usr/bin/env bash
# exit on error
set -o errexit

# Show Python & pip versions for debugging
python --version
pip --version
which python || true
which pip || true

# Debug database connection information
# Display DATABASE_URL without sensitive information
if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL (redacted):"
  echo "$DATABASE_URL" | sed 's/:[^:]*@/@/g'  # Redact password
else
  echo "DATABASE_URL is not set"
fi

# Try to parse the database host from DATABASE_URL for connectivity testing
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\(.*\):.*/\1/p')
  echo "Attempting to ping database host: $DB_HOST"
  # Try to ping database host (Render might block ICMP, but worth trying)
  ping -c 2 "$DB_HOST" || echo "Ping failed (this might be expected on Render)"
  # Try a DNS lookup to verify host resolution
  nslookup "$DB_HOST" || echo "DNS lookup failed"
fi

# Upgrade pip first
pip install --upgrade pip

# Install dependencies with verbose output to debug failures
pip install -r requirements.txt --verbose

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
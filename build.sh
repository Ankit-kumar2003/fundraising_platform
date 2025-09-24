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
  
  # Parse and display individual components of the DATABASE_URL for more detailed debugging
  echo "\nParsing DATABASE_URL components:"
  # Extract protocol
  DB_PROTOCOL=$(echo "$DATABASE_URL" | sed -n 's/\([^:]*\):\/\/.*$/\1/p')
  echo "Protocol: $DB_PROTOCOL"
  # Extract user and password (with password redacted)
  DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/\([^:]*\):.*@.*/\1/p')
  echo "User: $DB_USER"
  # Extract host
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\(.*\):.*/\1/p')
  echo "Host: $DB_HOST"
  # Extract port
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*@.*:\([0-9]*\)\/.*$/\1/p')
  echo "Port: $DB_PORT"
  # Extract database name
  DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
  echo "Database name: $DB_NAME"
else
  echo "DATABASE_URL is not set"
fi

# Try to parse the database host from DATABASE_URL for connectivity testing
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\(.*\):.*/\1/p')
  echo "\nAttempting to diagnose database connectivity:"
  echo "Host: $DB_HOST"
  
  # Try to ping database host (Render might block ICMP, but worth trying)
  echo "Pinging database host..."
  ping -c 2 "$DB_HOST" || echo "Ping failed (this might be expected on Render)"
  
  # Try a DNS lookup to verify host resolution
  echo "\nPerforming DNS lookup..."
  nslookup "$DB_HOST" || echo "DNS lookup failed"
  
  # Check if host is an IP address
  echo "\nChecking if host is an IP address..."
  if [[ $DB_HOST =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Host is an IP address: $DB_HOST"
  else
    echo "Host is a hostname: $DB_HOST"
    echo "Attempting to resolve hostname to IP..."
    HOST_IP=$(getent hosts "$DB_HOST" | awk '{print $1}')
    if [ -n "$HOST_IP" ]; then
      echo "Resolved to IP: $HOST_IP"
    else
      echo "Failed to resolve hostname to IP"
    fi
  fi
fi

# Check if we can connect to the port using nc (netcat)
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\(.*\):.*/\1/p')
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*@.*:\([0-9]*\)\/.*$/\1/p')
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    echo "\nAttempting to connect to $DB_HOST:$DB_PORT using nc..."
    nc -zv "$DB_HOST" "$DB_PORT" || echo "Connection to $DB_HOST:$DB_PORT failed"
  fi
fi

# Upgrade pip first
pip install --upgrade pip

# Install dependencies with verbose output to debug failures
pip install -r requirements.txt --verbose

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
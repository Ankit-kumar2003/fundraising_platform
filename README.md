# Fundraising Platform for Village Development

A Django-based web application designed to facilitate fundraising for village development projects, allowing donors to contribute to various initiatives and track their donations.

## Features
- User registration and authentication system
- Donation management and tracking
- Campaign creation and management
- User profile management
- Responsive design using Bootstrap 5

## Prerequisites
- Python 3.11.9 or later
- PostgreSQL (for production)
- SQLite (for development)

## Installation

### 1. Clone the repository
```bash
https://github.com/Ankit-kumar2003/fundraising_platform.git
cd fundraising_platform
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root directory and add the following variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (optional for development)
# DATABASE_URL=postgresql://user:password@host:port/database

# Email Configuration (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

The application should now be running at http://127.0.0.1:8000/

## Deployment to Render

This project includes a ready-to-use Render blueprint (`render.yaml`). You can deploy via the Render dashboard or CLI.

### Option A: One-click deploy from `render.yaml`
1. Ensure your code is pushed to GitHub.
2. In Render, create a new Web Service and select “Use existing Render YAML”.
3. Point to your repo containing `render.yaml`.
4. Render provisions a free Postgres DB and a free web service automatically.

The blueprint config includes:
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
- Start: `gunicorn auth_system.wsgi:application --bind 0.0.0.0:$PORT`
- Env vars: `DJANGO_SETTINGS_MODULE`, `SECRET_KEY` (generated), `DEBUG=False`, `ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1`, `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`
- Routes: static files rewrite for `/static/`

### Option B: Manual setup
1. Create a PostgreSQL database in Render and copy its `DATABASE_URL`.
2. Create a Web Service pointing to your GitHub repo.
3. Set environment variables:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
DATABASE_URL=your-render-postgresql-url
SECURE_SSL_REDIRECT=True
```
4. Build command: `./build.sh` or the inline command from the blueprint above.
5. Start command: `gunicorn auth_system.wsgi:application --bind 0.0.0.0:$PORT`

### Notes
- Static files are served via WhiteNoise in production.
- `SECURE_PROXY_SSL_HEADER` and `USE_X_FORWARDED_HOST` are configured for Render’s proxy.
- Password reset uses HTTPS in production and respects `RENDER_EXTERNAL_URL`.

## Push to GitHub
Run the following to commit and push all changes:
```bash
git add .
git commit -m "Prepare for Render deployment: settings, render.yaml, docs"
git push origin main
```

If your default branch is `master`:
```bash
git push origin master
```

## Project Structure
```
├── accounts/           # User authentication and account management
├── auth_system/        # Main project settings and configurations
├── features/           # Core application features and functionality
├── media/              # User-uploaded content storage
├── static/             # Static files (CSS, JavaScript, images)
├── templates/          # HTML templates
├── manage.py           # Django's command-line utility
├── requirements.txt    # Project dependencies
├── build.sh            # Build script for Render
├── Procfile            # Process configuration for Render
└── runtime.txt         # Python version specification
```

## License
This project is proprietary and intended for village development initiatives.

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

### 1. Set up a PostgreSQL database on Render
Create a new PostgreSQL database instance on Render and note the connection URL.

### 2. Configure environment variables on Render
Add the following environment variables to your Render deployment:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.onrender.com
DATABASE_URL=your-render-postgresql-url
SECURE_SSL_REDIRECT=True
```

### 3. Configure build settings
Render will automatically use the `build.sh` script and `runtime.txt` to set up your environment.

### 4. Configure the web service
Render will use the `Procfile` to run the application with Gunicorn.

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

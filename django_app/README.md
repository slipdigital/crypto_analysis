# Django App

A modern Django web application with Bootstrap 5 integration.

## Features

- Django 5.x framework
- Bootstrap 5.3.2 for responsive design
- Example CRUD functionality
- Django Admin integration
- Custom static files (CSS/JS)
- SQLite database (development)

## Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
django_app/
├── config/                 # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL routing
│   └── wsgi.py
├── main/                   # Main application
│   ├── __init__.py
│   ├── admin.py           # Admin configuration
│   ├── apps.py
│   ├── models.py          # Database models
│   ├── urls.py            # App URLs
│   └── views.py           # Views/Controllers
├── static/                 # Static files
│   ├── css/
│   │   └── custom.css     # Custom styles
│   ├── js/
│   │   └── custom.js      # Custom JavaScript
│   └── images/
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── main/              # Main app templates
│       ├── home.html
│       ├── about.html
│       ├── example_list.html
│       ├── example_detail.html
│       └── example_form.html
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## Available Pages

- **Home** (`/`) - Landing page with overview
- **About** (`/about/`) - About page with tech stack info
- **Examples** (`/examples/`) - List of example items
- **Example Detail** (`/examples/<id>/`) - Detail view of an example
- **Create Example** (`/examples/new/`) - Form to create new example
- **Admin** (`/admin/`) - Django admin interface

## Bootstrap Integration

The application uses Bootstrap 5.3.2 via CDN with:
- Responsive navigation bar
- Card layouts
- Forms with Bootstrap styling
- Alerts and messages
- Pagination
- Icons (Bootstrap Icons)

## Customization

### Adding New Models

1. Define model in `main/models.py`
2. Create and run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Register in `main/admin.py`

### Adding New Views

1. Create view in `main/views.py`
2. Add URL pattern in `main/urls.py`
3. Create corresponding template in `templates/main/`

### Custom Styling

- Edit `static/css/custom.css` for custom styles
- Edit `static/js/custom.js` for custom JavaScript

## Development

To make changes to the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

To create a new Django app:

```bash
python manage.py startapp app_name
```

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in settings.py
2. Update `SECRET_KEY` with a secure random key
3. Configure `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL, MySQL, etc.)
5. Set up proper static file serving
6. Configure HTTPS
7. Use environment variables for sensitive settings

## License

This project is open source and available for educational purposes.

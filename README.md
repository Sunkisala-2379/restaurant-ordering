# Smart Restaurant Food Ordering & Kitchen Dashboard

A production-ready full-stack web application for restaurant food ordering with a real-time kitchen dashboard. Built with Django, Bootstrap 5, and vanilla JavaScript.

## Project Overview

Smart Restaurant is a modern ordering platform where customers can browse menus, manage a shopping cart, place orders, and track order status in real time. Kitchen staff use a protected dashboard to update order statuses with one-click actions.

### Key Features

- **Customer Portal**: Browse menu, search, filter by category/diet, shopping cart with localStorage + session sync
- **Checkout**: CSRF-protected order placement with form validation
- **Order Tracking**: Live status timeline with auto-refresh every 5 seconds
- **Kitchen Dashboard**: Staff-only page to manage pending orders
- **Admin Panel**: Full CRUD for categories, menu items, orders, and order items

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 5.x |
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Database | SQLite (development), Django ORM |
| Deployment | Gunicorn, WhiteNoise, Render |

## Installation

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd restaurant_ordering

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Migration

```bash
python manage.py migrate
```

## Seed Sample Data

```bash
python manage.py seed_menu
```

This populates categories and menu items for development and demo purposes.

## Run Server

```bash
python manage.py runserver 8080
```

Or on Windows:

```powershell
.\run.bat
```

Visit `http://127.0.0.1:8080/` in your browser.

## Create Superuser

### Option 1: Automated Script

```bash
python create_superuser.py
```

Default credentials (development):
- **Username**: admin
- **Password**: admin12345

### Option 2: Django Management Command

```bash
python manage.py createsuperuser
```

The kitchen dashboard requires a staff account. Superusers automatically have staff access.

## Deployment on Render

1. Push the repository to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your repository
4. Render will use `render.yaml` for configuration
5. Set environment variables:
   - `ALLOWED_HOSTS` — your Render domain (e.g. `smart-restaurant.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` — `https://smart-restaurant.onrender.com`
6. Deploy

The build command automatically runs migrations, creates a superuser, and seeds menu data.

## Folder Structure

```
restaurant_ordering/
├── manage.py
├── requirements.txt
├── runtime.txt
├── render.yaml
├── Procfile
├── create_superuser.py
├── README.md
├── restaurant_ordering/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── restaurant/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── context_processors.py
│   └── management/commands/seed_menu.py
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   ├── home.html
│   ├── menu.html
│   ├── cart.html
│   ├── checkout.html
│   ├── success.html
│   ├── tracking.html
│   ├── kitchen_dashboard.html
│   ├── 404.html
│   └── 500.html
└── static/
    ├── css/style.css
    └── js/
        ├── cart.js
        ├── tracking.js
        ├── search.js
        ├── category-filter.js
        └── checkout.js
```

## Screenshots

> Placeholder — add screenshots of the home page, menu, cart, checkout, order tracking, and kitchen dashboard here.

| Page | Screenshot |
|------|-----------|
| Home | `screenshots/home.png` |
| Menu | `screenshots/menu.png` |
| Cart | `screenshots/cart.png` |
| Order Tracking | `screenshots/tracking.png` |
| Kitchen Dashboard | `screenshots/kitchen.png` |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Dev key (change in production) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins | `http://localhost:8080` |
| `DEV_PORT` | Local development server port | `8080` |
| `DJANGO_SUPERUSER_USERNAME` | Admin username | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | `admin@smartrestaurant.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | `admin12345` |

## License

MIT

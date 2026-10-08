# Sustainify

Sustainify is an e-commerce project focused on making more sustainable shopping choices easier to discover. It brings customers and vendors together through a marketplace where vendors can provide ISO 14001 certification documentation.

Customers can browse and search products, filter by category or tags, manage a cart, place orders, and review products. Vendors can register, manage product listings, and provide business and certification information.

## Tech stack

- **Language:** Python
- **Web framework:** Django 5.1
- **Database:** SQLite by default
- **Frontend:** Django templates, HTML, CSS, and JavaScript
- **Payments:** Stripe Checkout using the Stripe Python SDK
- **Other libraries:** django-taggit, django-jazzmin, shortuuid, PyPDF2, and python-dotenv

## Architecture

The project follows Django's project-and-app structure:

- `ecomprj/` contains project configuration, root URL routing, and ASGI/WSGI entry points.
- `core/` contains the main commerce domain: product, category, vendor, cart, order, review, and certificate models; storefront and dashboard views; forms; and app routes.
- `userauths/` contains the custom user model, user profiles, contact form model, and sign-up/sign-in/sign-out views.
- `templates/` contains the Django HTML templates, organized into app pages and shared partials.
- `static/` contains frontend assets such as stylesheets, scripts, and images.
- `media/` is Django's local upload location. Category and product-image assets are kept in the repository; user and vendor uploads are excluded by `.gitignore`.
- `core/migrations/` and `userauths/migrations/` contain Django's database schema history. Keep these source files in version control so new installations can build and update the database.

Requests are routed from `ecomprj/urls.py` to the `core` or `userauths` app. Views coordinate forms, models, and templates. Django's configured custom user model is `userauths.User`, which uses email as its login identifier.

### Product eco score

Each product receives a project-specific score from 0 to 10. Sustainify calculates it from product data for carbon footprint, material sourcing, recyclability, water use, energy efficiency, biodegradability, and durability. The factors are weighted in the application, with durability contributing up to 10% of the total.

**Disclaimer:** The eco score is Sustainify's own project-specific calculation. It is not a certified environmental assessment, an official rating, or a guarantee of a product's environmental impact. Vendor-provided ISO 14001 certification documentation is separate from the product eco score.

### Stripe payment flow

The checkout view creates an order, and the Stripe payment view creates a Stripe Checkout Session for that order. The customer is redirected to Stripe Checkout to pay by card. On return, the application retrieves the Checkout Session and marks the order as paid when Stripe reports a paid status. The checkout uses INR and requires Stripe API credentials in the local environment configuration.

## Prerequisites

- Windows with PowerShell
- Python 3.13 (the version used by the current project virtual environment)
- Git, if cloning the repository
- Stripe test credentials for testing the payment flow

## Setup on Windows

Open PowerShell in the project root (the directory containing `manage.py`).

1. Create a virtual environment:

   ```powershell
   py -3.13 -m venv .venv
   ```

2. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation for this terminal, allow scripts for the current process and activate again:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned project dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   In VS Code, the workspace settings select `.venv` as the interpreter and enable automatic activation for new integrated terminals.

## Environment configuration

Create a `.env` file in the project root, alongside `manage.py`. Django loads it through `python-dotenv`. The `.env` file is ignored by Git; do not commit real credentials.

Add the settings below, replacing placeholder values with your own credentials:

```dotenv
SECRET_KEY=replace-with-a-long-random-django-secret
STRIPE_SECRET_KEY=sk_test_replace_with_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_test_replace_with_your_stripe_publishable_key
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
DEFAULT_FROM_EMAIL=Sustainify <no-reply@example.com>

MAILGUN_API_KEY=
MAILGUN_SENDER_DOMAIN=
```

Use Stripe test-mode credentials for local development. Never put secret keys, passwords, or production credentials in source code or commit them to the repository. For deployment, set `DEBUG=False`, use a strong unique `SECRET_KEY`, and configure `ALLOWED_HOSTS` with the deployed hostnames.

## Initialize and run

Run these commands from the project root with the virtual environment activated:

```powershell
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. The Django admin is at `http://127.0.0.1:8000/admin/`.

To run the user-authentication app tests:

```powershell
python manage.py test userauths
```

## Data and version control

The local SQLite database (`db.sqlite3`), `.env`, log files, Python cache files, and machine-specific IDE settings are excluded by `.gitignore`. A fresh checkout creates its database by running `python manage.py migrate`; it does not include local users or orders. Uploaded user/vendor media is also ignored, so configure persistent media storage separately for a deployed application.

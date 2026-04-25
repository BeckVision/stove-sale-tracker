# stove-sale-tracker

Django web app for tracking daily stove sales, production output, worker earnings, investor shares, and profit calculations.

The app is designed for a small production/sales workflow where staff record product sales, workers log production quantities, and investors can view their earnings.

## Features

- Staff sale entry with product, quantity, and total sale price
- Product-level base cost and master/worker fee configuration
- Investor share tracking based on profit after base cost
- Worker production logs with per-product pay rates
- Staff revenue dashboard for today, this week, this month, and all-time sales
- Investor and worker dashboards with daily and weekly earnings
- Uzbek-language interface and messages
- Local SQLite development with `DATABASE_URL` support for PostgreSQL deployments

## Stack

- Python
- Django 5
- SQLite for local development
- PostgreSQL-compatible deployment through `dj-database-url`
- Gunicorn and WhiteNoise for production serving

## Data Model

```text
Product
  -> Sale
  -> WorkerPayRate
  -> ProductionLog

User
  -> Investor
  -> Worker
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Run migrations and create an admin user:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key for the environment |
| `DJANGO_DEBUG` | No | Set to `True` for local development |
| `ALLOWED_HOSTS` | No | Comma-separated hostnames, defaults to localhost |
| `DATABASE_URL` | No | PostgreSQL connection URL for deployment |

## Public Repository Hygiene

Local database files are intentionally ignored. Use migrations and seed/admin data instead of committing `db.sqlite3`.

## License

MIT. See [LICENSE](LICENSE).

# Meal Mate

A Django food ordering demo with restaurant menus, a cart, and Razorpay checkout.

## Run locally

Use Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

## Razorpay test payments

Checkout requires Razorpay test credentials. Set them in your terminal before
starting the server; never commit real credentials:

```bash
export RAZORPAY_KEY_ID="rzp_test_your_key_id"
export RAZORPAY_KEY_SECRET="your_razorpay_test_secret"
python manage.py runserver
```

If the credentials are not configured, the rest of the site remains usable,
but checkout displays a configuration message instead of opening payment.

## Notes

- The SQLite database is local-only and excluded from Git. Run migrations to
  create a fresh local database.
- `DEBUG` is enabled for local development. Configure production settings and
  secrets before deploying.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first (their own cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then the application code
COPY . .

# Collect static files at build time
RUN DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput

# Production server — NOT runserver
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY dev_django/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY dev_django/ .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "dev_django.wsgi:application", "--bind", "0.0.0.0:8000"]

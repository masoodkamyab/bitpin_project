#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User;
import os;

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=email)
"

echo "Starting server..."
exec "$@"

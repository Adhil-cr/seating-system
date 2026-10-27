#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running database migrations..."
python core/manage.py migrate --noinput

echo "==> Collecting static files..."
python core/manage.py collectstatic --noinput

echo "==> Build completed successfully!"
